from argparse import Namespace
from logging import getLogger
import pandas as pd
from scipy import interpolate

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper
from src.magnetopy.magnetopy_utils.magnetopy_conversions_helper import MagnetoPyConversionsHelper
from src.magnetopy.magnetopy_utils.magnetopy_igrf_helper import MagnetoPyIGRFHelper

class CalculateIGRF:
    def __init__(self, arguments: Namespace):
        self.__magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='CalculateIGRF')

        self.project_name: str = arguments.project_name
        self.stations_file: str = arguments.stations_file
        self.stations_cols: str = arguments.stations_cols
        self.altitude: float = arguments.altitude
        self.date: str = arguments.date
        
        self.__calculate_igrf()

    def __calculate_igrf(self) -> None:
        """
        Performs the IGRF correction to a data set based on the 13th generation coefficients.

        :return: Nothing to return
        :rtype: None
        """
        self.__magnetopy_logging.info('Performing the IGRF correction')

        _project_name = self.project_name
        _stations_file_path = self.stations_file
        _stations_cols = self.stations_cols.split(',')
        _altitude = self.altitude
        _date = self.date

        # Create an instance of the MagnetoPyIGRFHelper class
        magnetopyIGRFHelper = MagnetoPyIGRFHelper()

        igrf = magnetopyIGRFHelper.load_igrf_coefficients()

        stations_df = MagnetoPyFilesHelper.read_and_verify_columns(_stations_file_path, _stations_cols)

        stations_df[_stations_cols[0]] = stations_df[_stations_cols[0]].apply(lambda x: MagnetoPyFilesHelper.validate_date(x))
        stations_df[_stations_cols[1]] = stations_df[_stations_cols[1]].apply(lambda x: MagnetoPyFilesHelper.validate_time(x))
        stations_df['datetime'] = pd.to_datetime(stations_df[_stations_cols[0]] + ' ' + stations_df[_stations_cols[1]])

        stations_df['decimal_date'] = stations_df[_stations_cols[0]].apply(lambda x: MagnetoPyConversionsHelper.convert_date_to_decimal_date(x))

        # Get the unique dates in the stations_df dataframe
        #unique_dates = stations_df['decimal_date'].unique()

        # Convert the unique dates to a numpy array
        #unique_dates = unique_dates.astype(float)

        date = MagnetoPyConversionsHelper.convert_date_to_decimal_date(_date)

        lat_avg = stations_df[_stations_cols[2]].mean()
        lon_avg = stations_df[_stations_cols[3]].mean()

        colat = 90 - lat_avg

        alt, colat, sd, cd = magnetopyIGRFHelper.gg_to_geo(_altitude, colat)

        f = interpolate.interp1d(igrf.time, igrf.coeffs, fill_value='extrapolate')
        coeffs = f(date)

        B_radius, B_theta, B_phi = magnetopyIGRFHelper.synth_values(coeffs.T, alt, colat, lon_avg, igrf.parameters['nmax'])

        #for date in unique_dates:
        epoch = (date - 1900) // 5
        epoch_start = epoch * 5

        coeffs_sv = f(1900 + epoch_start + 1) - f(1900 + epoch_start)
        Brs, Bts, Bps = magnetopyIGRFHelper.synth_values(coeffs_sv.T, alt, colat, lon_avg, igrf.parameters['nmax'])

        coeffsm = f(1900 + epoch_start)
        Brm, Btm, Bpm = magnetopyIGRFHelper.synth_values(coeffsm.T, alt, colat, lon_avg, igrf.parameters['nmax'])

        X = -B_theta
        Y = B_phi
        Z = -B_radius

        dX = -Bts
        dY = Bps
        dZ = -Brs

        Xm = -Btm
        Ym = Bpm
        Zm = -Brm

        # Rotate back to geodetic coordinates if necessary
        t = X
        X = X * cd + Z * sd
        Z = Z * cd - t * sd

        t = dX
        dX = dX * cd + dZ * sd
        dZ = dZ * cd - t * sd

        t = Xm
        Xm = Xm * cd + Zm * sd
        Zm = Zm * cd - t * sd

        # Compute the four non-linear components
        dec, hoz, inc, eff = magnetopyIGRFHelper.xyz2dhif(X, Y, Z)

        # The IGRF SV coefficients are relative to the main field components
        # at the start of each five year epoch e. g. 2010, 2015, 2020.
        decs, hozs, incs, effs = magnetopyIGRFHelper.xyz2dhif_sv(Xm, Ym, Zm, dX, dY, dZ)

        # Convert the results to a dictionary as above
        degree_sign= u'\N{DEGREE SIGN}'
        results = {
            'igrf_date': date,
            f'D({degree_sign})': dec,
            f'I({degree_sign})': inc,
            'H(nT)': hoz,
            'F(nT)': eff,
            'X(nT)': X,
            'Y(nT)': Y,
            'Z(nT)': Z,
            'SV_D(min/yr)': decs,
            'SV_I(min/yr)': incs,
            'SV_H(nT/yr)': hozs,
            'SV_F(nT/yr)': effs,
            'SV_X(nT/yr)': dX,
            'SV_Y(nT/yr)': dY,
            'SV_Z(nT/yr)': dZ
        }

        output_df = MagnetoPyFilesHelper.write_igrf_components_to_dataframe(stations_df, results)

        MagnetoPyFilesHelper.save_data(output_df, _project_name)

        self.__magnetopy_logging.info('IGRF correction completed')

        return None