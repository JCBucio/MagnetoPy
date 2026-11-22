from argparse import Namespace
from logging import getLogger
import os
import pandas as pd

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper


def run_diurnal_variation(arguments: Namespace) -> None:
    """
    Performs the correction for diurnal variation in the entered data set.

    Reads survey station and base station CSVs, matches each survey
    measurement to its nearest base-station reading in time using
    pd.merge_asof, computes diurnal variation and the corrected field,
    then saves the result to resources/<project_name>/.

    :param arguments: Parsed CLI namespace
    :return: None
    """
    log: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='DiurnalVariation')
    log.info('Validating datasets and columns')

    _stations_file_path = arguments.stations_file
    _base_station_file_path = arguments.base_station_file
    _project_name = getattr(arguments, 'project_name', None) or os.path.splitext(os.path.basename(_stations_file_path))[0]

    raw_stations_df = pd.read_csv(_stations_file_path, nrows=5)
    raw_base_df = pd.read_csv(_base_station_file_path, nrows=5)

    stations_cols_arg = getattr(arguments, 'stations_cols', None)
    if stations_cols_arg:
        _stations_cols = [col.strip() for col in stations_cols_arg.split(',')]
    else:
        _stations_cols = MagnetoPyFilesHelper.detect_stations_columns(raw_stations_df.columns)
        log.info(f'Auto-detected survey stations columns: {_stations_cols}')

    base_station_cols_arg = getattr(arguments, 'base_station_cols', None)
    if base_station_cols_arg:
        _base_station_cols = [col.strip() for col in base_station_cols_arg.split(',')]
    else:
        _base_station_cols = MagnetoPyFilesHelper.detect_base_station_columns(raw_base_df.columns)
        log.info(f'Auto-detected base station columns: {_base_station_cols}')

    if len(_stations_cols) < 5:
        raise ValueError(
            "stations_cols requires 5 comma-separated columns in order: "
            "date, time, latitude, longitude, magnetic_field"
        )
    if len(_base_station_cols) < 3:
        raise ValueError(
            "base_station_cols requires 3 comma-separated columns in order: "
            "date, time, magnetic_field"
        )

    stations_df = MagnetoPyFilesHelper.read_and_verify_columns(_stations_file_path, _stations_cols)
    base_stations_df = MagnetoPyFilesHelper.read_and_verify_columns(_base_station_file_path, _base_station_cols)
    if stations_df is None or base_stations_df is None:
        log.error('Error reading the input files or verifying columns')
        return

    stations_df[_stations_cols[0]] = stations_df[_stations_cols[0]].apply(lambda x: MagnetoPyFilesHelper.validate_date(x))
    stations_df[_stations_cols[1]] = stations_df[_stations_cols[1]].apply(lambda x: MagnetoPyFilesHelper.validate_time(x))
    stations_df['datetime'] = pd.to_datetime(stations_df[_stations_cols[0]] + ' ' + stations_df[_stations_cols[1]])

    base_stations_df[_base_station_cols[0]] = base_stations_df[_base_station_cols[0]].apply(lambda x: MagnetoPyFilesHelper.validate_date(x))
    base_stations_df[_base_station_cols[1]] = base_stations_df[_base_station_cols[1]].apply(lambda x: MagnetoPyFilesHelper.validate_time(x))
    base_stations_df['datetime'] = pd.to_datetime(base_stations_df[_base_station_cols[0]] + ' ' + base_stations_df[_base_station_cols[1]])

    base_mag_numeric = pd.to_numeric(base_stations_df[_base_station_cols[2]], errors='coerce')
    base_stations_df['magfield_mean'] = base_mag_numeric.groupby(base_stations_df[_base_station_cols[0]]).transform('mean')

    stations_df, base_stations_df = MagnetoPyFilesHelper.rename_columns(stations_df, base_stations_df)

    log.info('Performing the diurnal variation correction')

    stations_df = stations_df.reset_index(drop=True)
    stations_df['__order__'] = stations_df.index
    stations_sorted = stations_df.sort_values('sta_datetime')
    base_sorted = base_stations_df.sort_values('base_datetime')

    result_df = pd.merge_asof(
        stations_sorted,
        base_sorted,
        left_on='sta_datetime',
        right_on='base_datetime',
        direction='nearest'
    )

    result_df['time_diff'] = (result_df['base_datetime'] - result_df['sta_datetime']).abs()
    result_df = result_df.sort_values('__order__').drop(columns=['__order__']).reset_index(drop=True)

    max_gap = result_df['time_diff'].max()
    if max_gap > pd.Timedelta(hours=1):
        log.warning(
            f'Large time difference detected between survey and base records: maximum gap is {max_gap}.'
        )

    base_mag = pd.to_numeric(result_df['base_' + _base_station_cols[2]], errors='coerce')
    base_mean = pd.to_numeric(result_df['base_magfield_mean'], errors='coerce')
    sta_mag = pd.to_numeric(result_df['sta_' + _stations_cols[4]], errors='coerce')

    result_df['diurnal_var'] = base_mag - base_mean
    result_df['diurnal_var_corr'] = sta_mag - result_df['diurnal_var']

    log.info(f'Total records: {len(result_df)}')

    MagnetoPyFilesHelper.save_data(result_df, _project_name)

    log.info('Diurnal variation correction completed')
