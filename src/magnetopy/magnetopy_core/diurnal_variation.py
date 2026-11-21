from argparse import Namespace
from logging import getLogger
import pandas as pd

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper

class DiurnalVariation:
    def __init__(self, arguments: Namespace):
        self.__magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='DiurnalVariation')

        self.project_name: str = arguments.project_name
        self.stations_file: str = arguments.stations_file
        self.stations_cols: str = arguments.stations_cols
        self.base_station_file: str = arguments.base_station_file
        self.base_station_cols: str = arguments.base_station_cols

        self.__diurnal_variation()

    def __diurnal_variation(self) -> None:
        """
        Performs the correction for diurnal variation in the entered data set.

        :return: Nothing to return
        :rtype: None
        """
        self.__magnetopy_logging.info('Validating datasets and columns')

        _project_name = self.project_name
        _stations_file_path = self.stations_file
        _stations_cols = [col.strip() for col in self.stations_cols.split(',')]
        _base_station_file_path = self.base_station_file
        _base_station_cols = [col.strip() for col in self.base_station_cols.split(',')]

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
            self.__magnetopy_logging.error('Error reading the input files or verifying columns')
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
        
        self.__magnetopy_logging.info('Performing the diurnal variation correction')

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
            self.__magnetopy_logging.warning(
                f'Large time difference detected between survey and base records: maximum gap is {max_gap}.'
            )

        base_mag = pd.to_numeric(result_df['base_' + _base_station_cols[2]], errors='coerce')
        base_mean = pd.to_numeric(result_df['base_magfield_mean'], errors='coerce')
        sta_mag = pd.to_numeric(result_df['sta_' + _stations_cols[4]], errors='coerce')

        result_df['diurnal_var'] = base_mag - base_mean
        result_df['diurnal_var_corr'] = sta_mag - result_df['diurnal_var']

        self.__magnetopy_logging.info(f'Total records: {len(result_df)}')

        MagnetoPyFilesHelper.save_data(result_df, _project_name)

        self.__magnetopy_logging.info('Diurnal variation correction completed')