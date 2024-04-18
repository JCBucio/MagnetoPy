from argparse import Namespace
from logging import getLogger
import pandas as pd

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper

class DiurnalVariation:
    def __init__(self, arguments: Namespace):
        self.__magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='DiurnalVariation')

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

        _stations_file_path = self.stations_file
        _stations_cols = self.stations_cols.split(',')
        _base_station_file_path = self.base_station_file
        _base_station_cols = self.base_station_cols.split(',')

        stations_df = MagnetoPyFilesHelper.read_and_verify_columns(_stations_file_path, _stations_cols)
        base_stations_df = MagnetoPyFilesHelper.read_and_verify_columns(_base_station_file_path, _base_station_cols)

        stations_df[_stations_cols[0]] = stations_df[_stations_cols[0]].apply(lambda x: MagnetoPyFilesHelper.validate_date(x))
        stations_df[_stations_cols[1]] = stations_df[_stations_cols[1]].apply(lambda x: MagnetoPyFilesHelper.validate_time(x))
        stations_df['datetime'] = pd.to_datetime(stations_df[_stations_cols[0]] + ' ' + stations_df[_stations_cols[1]])
        
        base_stations_df[_base_station_cols[0]] = base_stations_df[_base_station_cols[0]].apply(lambda x: MagnetoPyFilesHelper.validate_date(x))
        base_stations_df[_base_station_cols[1]] = base_stations_df[_base_station_cols[1]].apply(lambda x: MagnetoPyFilesHelper.validate_time(x))
        base_stations_df['datetime'] = pd.to_datetime(base_stations_df[_base_station_cols[0]] + ' ' + base_stations_df[_base_station_cols[1]])
        
        self.__magnetopy_logging.info('Performing the diurnal variation correction')

        records = []

        for index, row in stations_df.iterrows():
            stations_datetime = row['datetime']

            base_stations_df['time_diff'] = abs(base_stations_df['datetime'] - stations_datetime)

            closest_index = base_stations_df['time_diff'].idxmin()
            closest_record = base_stations_df.loc[closest_index]

            records.append(closest_record)

        result_df = pd.DataFrame(records)

        print(result_df.head())

        self.__magnetopy_logging.info(f'Total records: {len(result_df)}')

        self.__magnetopy_logging.info('Diurnal variation correction completed')

        return result_df