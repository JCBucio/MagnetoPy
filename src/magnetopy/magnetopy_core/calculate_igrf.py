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

        self.stations_file: str = arguments.stations_file
        self.stations_cols: str = arguments.stations_cols
        
        self.__calculate_igrf()

    def __calculate_igrf(self) -> None:
        """
        Performs the IGRF correction to a data set based on the 13th generation coefficients.

        :return: Nothing to return
        :rtype: None
        """
        self.__magnetopy_logging.info('Performing the IGRF correction')

        _stations_file_path = self.stations_file
        _stations_cols = self.stations_cols.split(',')

        igrf = MagnetoPyIGRFHelper().load_igrf_coefficients()

        f = interpolate.interp1d(igrf.time, igrf.coeffs, fill_value='extrapolate')

        stations_df = MagnetoPyFilesHelper.read_and_verify_columns(_stations_file_path, _stations_cols)

        stations_df[_stations_cols[0]] = stations_df[_stations_cols[0]].apply(lambda x: MagnetoPyFilesHelper.validate_date(x))
        stations_df[_stations_cols[1]] = stations_df[_stations_cols[1]].apply(lambda x: MagnetoPyFilesHelper.validate_time(x))
        stations_df['datetime'] = pd.to_datetime(stations_df[_stations_cols[0]] + ' ' + stations_df[_stations_cols[1]])

        stations_df['decimal_date'] = stations_df[_stations_cols[0]].apply(lambda x: MagnetoPyConversionsHelper.convert_date_to_decimal_date(x))

        self.__magnetopy_logging.info('Stations columns:')
        self.__magnetopy_logging.info(stations_df.columns)

        self.__magnetopy_logging.info('Stations dataframe:')
        self.__magnetopy_logging.info(stations_df.head())

        return None