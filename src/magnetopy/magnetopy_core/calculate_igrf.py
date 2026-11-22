from argparse import Namespace
from logging import getLogger
import os
import pandas as pd
from scipy import interpolate

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper
from src.magnetopy.magnetopy_utils.magnetopy_conversions_helper import MagnetoPyConversionsHelper
from src.magnetopy.magnetopy_utils.magnetopy_igrf_helper import MagnetoPyIGRFHelper


def _build_igrf_results(date: str, verbose: bool,
                        dec, hoz, inc, eff, X, Y, Z,
                        decs, hozs, incs, effs, dX, dY, dZ) -> dict:
    """
    Build the output IGRF result dictionary.

    Default mode includes the principal field components only.
    Verbose mode additionally includes the secular variation columns.
    """
    degree_sign = u'\N{DEGREE SIGN}'
    results = {
        'igrf_date': date,
        f'D({degree_sign})': dec,
        f'I({degree_sign})': inc,
        'H(nT)': hoz,
        'F(nT)': eff,
        'X(nT)': X,
        'Y(nT)': Y,
        'Z(nT)': Z,
    }

    if verbose:
        results.update({
            'SV_D(min/yr)': decs,
            'SV_I(min/yr)': incs,
            'SV_H(nT/yr)': hozs,
            'SV_F(nT/yr)': effs,
            'SV_X(nT/yr)': dX,
            'SV_Y(nT/yr)': dY,
            'SV_Z(nT/yr)': dZ,
        })

    return results


def run_calculate_igrf(arguments: Namespace) -> None:
    """
    Performs the IGRF correction to a data set based on the IGRF-14 coefficients
    and computes the total magnetic anomaly (observed field minus F_IGRF).

    :param arguments: Parsed CLI namespace
    :return: None
    """
    log: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='CalculateIGRF')
    log.info('Performing the IGRF correction')

    _stations_file_path = arguments.stations_file
    _project_name = getattr(arguments, 'project_name', None) or os.path.splitext(os.path.basename(_stations_file_path))[0]
    _altitude = arguments.altitude
    _date_arg = getattr(arguments, 'date', None)
    _verbose = getattr(arguments, 'verbose', False)

    raw_stations_df = pd.read_csv(_stations_file_path, nrows=5)
    stations_cols_arg = getattr(arguments, 'stations_cols', None)
    if stations_cols_arg:
        _stations_cols = [col.strip() for col in stations_cols_arg.split(',')]
    else:
        _stations_cols = MagnetoPyFilesHelper.detect_stations_columns(raw_stations_df.columns)
        log.info(f'Auto-detected survey stations columns: {_stations_cols}')

    if len(_stations_cols) < 5:
        raise ValueError(
            "stations_cols requires 5 comma-separated columns in order: "
            "date, time, latitude, longitude, magnetic_field"
        )

    igrf_helper = MagnetoPyIGRFHelper()
    igrf = igrf_helper.load_igrf_coefficients()

    stations_df = MagnetoPyFilesHelper.read_and_verify_columns(_stations_file_path, _stations_cols)
    if stations_df is None:
        log.error('Error reading the stations file or verifying columns')
        return

    stations_df[_stations_cols[0]] = stations_df[_stations_cols[0]].apply(lambda x: MagnetoPyFilesHelper.validate_date(x))
    stations_df[_stations_cols[1]] = stations_df[_stations_cols[1]].apply(lambda x: MagnetoPyFilesHelper.validate_time(x))
    stations_df['datetime'] = pd.to_datetime(stations_df[_stations_cols[0]] + ' ' + stations_df[_stations_cols[1]])

    stations_df['decimal_date'] = stations_df[_stations_cols[0]].apply(lambda x: MagnetoPyConversionsHelper.convert_date_to_decimal_date(x))

    # Auto-detect date from first record if omitted
    if not _date_arg:
        _date = str(stations_df[_stations_cols[0]].iloc[0])
        log.info(f'Auto-detected survey date from data: {_date}')
    else:
        _date = _date_arg

    date = MagnetoPyConversionsHelper.convert_date_to_decimal_date(_date)

    lat_avg = pd.to_numeric(stations_df[_stations_cols[2]], errors='coerce').mean()
    lon_avg = pd.to_numeric(stations_df[_stations_cols[3]], errors='coerce').mean()

    colat = 90 - lat_avg
    alt, colat, sd, cd = igrf_helper.gg_to_geo(_altitude, colat)

    f = interpolate.interp1d(igrf.time, igrf.coeffs, fill_value='extrapolate')
    coeffs = f(date)

    B_radius, B_theta, B_phi = igrf_helper.synth_values(coeffs.T, alt, colat, lon_avg, igrf.parameters['nmax'])

    epoch = (date - 1900) // 5
    epoch_start = epoch * 5

    coeffs_sv = f(1900 + epoch_start + 1) - f(1900 + epoch_start)
    Brs, Bts, Bps = igrf_helper.synth_values(coeffs_sv.T, alt, colat, lon_avg, igrf.parameters['nmax'])

    coeffsm = f(1900 + epoch_start)
    Brm, Btm, Bpm = igrf_helper.synth_values(coeffsm.T, alt, colat, lon_avg, igrf.parameters['nmax'])

    X = -B_theta
    Y = B_phi
    Z = -B_radius

    dX = -Bts
    dY = Bps
    dZ = -Brs

    Xm = -Btm
    Ym = Bpm
    Zm = -Brm

    # Rotate back to geodetic coordinates
    t = X
    X = X * cd + Z * sd
    Z = Z * cd - t * sd

    t = dX
    dX = dX * cd + dZ * sd
    dZ = dZ * cd - t * sd

    t = Xm
    Xm = Xm * cd + Zm * sd
    Zm = Zm * cd - t * sd

    dec, hoz, inc, eff = igrf_helper.xyz2dhif(X, Y, Z)
    decs, hozs, incs, effs = igrf_helper.xyz2dhif_sv(Xm, Ym, Zm, dX, dY, dZ)

    results = _build_igrf_results(
        date=_date, verbose=_verbose,
        dec=dec, hoz=hoz, inc=inc, eff=eff,
        X=X, Y=Y, Z=Z,
        decs=decs, hozs=hozs, incs=incs, effs=effs,
        dX=dX, dY=dY, dZ=dZ,
    )

    output_df = MagnetoPyFilesHelper.write_igrf_components_to_dataframe(stations_df, results)

    # Total magnetic anomaly: observed field minus IGRF total intensity F
    mag_observed = pd.to_numeric(output_df[_stations_cols[4]], errors='coerce')
    output_df['mag_anomaly(nT)'] = mag_observed - results['F(nT)']

    MagnetoPyFilesHelper.save_data(output_df, _project_name)

    log.info('IGRF correction completed')
