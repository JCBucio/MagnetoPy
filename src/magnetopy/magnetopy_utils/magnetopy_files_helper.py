import os
import re
import pandas as pd
from datetime import datetime
from logging import getLogger

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging


class MagnetoPyFilesHelper:
    @staticmethod
    def validate_date(date_str):
        """
        This function validates the date string and returns the date object.

        :param date_str: str
        :return: datetime.date
        """
        magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetoPyFilesHelper: validate_date')
        formats = ['%d-%m-%Y', '%d/%m/%Y', '%d%m%Y', '%Y-%m-%d', '%Y/%m/%d', '%m-%d-%Y', '%m/%d/%Y', '%Y.%m.%d']
        for fmt in formats:
            try:
                new_date = datetime.strptime(date_str, fmt).date()
                return new_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        raise ValueError("Invalid date format: {}".format(date_str))

    @staticmethod
    def validate_time(time_str):
        """
        This function validates the time string and returns the time object.

        :param time_str: str
        :return: datetime.time
        """
        magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetoPyFilesHelper: validate_time')
        formats = ['%H:%M:%S', '%I:%M:%S %p', '%H%M%S', '%I:%M %p', '%I:%M:%S']
        for fmt in formats:
            try:
                new_time = datetime.strptime(str(time_str), fmt).time()
                return new_time.strftime('%H:%M:%S')
            except ValueError:
                continue
        raise ValueError("Invalid time format: {}".format(time_str))
    
    @staticmethod
    def check_lat_bounds(lat):
        """
        This function checks the latitude bounds and returns the latitude object.

        :param lat: float
        :return: float
        """
        if -90 <= lat <= 90:
            return lat
        raise ValueError("Latitude out of bounds: {}".format(lat))
    
    @staticmethod
    def check_lon_bounds(lon):
        """
        This function checks the longitude bounds and returns the longitude object.

        :param lon: float
        :return: float
        """
        if -180 <= lon <= 180:
            return lon
        raise ValueError("Longitude out of bounds: {}".format(lon))
    
    @staticmethod
    def read_and_verify_columns(file_path, columns):
        """
        This function reads the file from the given path and verifies the columns in the dataset.

        :param file_path: str
        :param columns: list
        :return: pd.DataFrame
        """
        magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetoPyFilesHelper: read_and_verify_columns')
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            print("Error: File not found at path:", file_path)
            magnetopy_logging.error(f'Error: File not found at path: "{file_path}"')
            return None
        except Exception as e:
            magnetopy_logging.error(f'Error: "{e}"')
            return None

        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            magnetopy_logging.error(f'Error: Columns not found in the dataset: "{missing_columns}"')
            return None

        return df[columns]
    
    @staticmethod
    def rename_columns(stations_df, base_station_df):
        """
        This function renames the columns in the given dataframes adding sta_ and base_ prefixes.
        
        :param stations_df: pd.DataFrame
        :param base_station_df: pd.DataFrame
        :return: pd.DataFrame, pd.DataFrame
        """
        magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetoPyFilesHelper: rename_columns')
        stations_df.columns = ['sta_' + col for col in stations_df.columns]
        base_station_df.columns = ['base_' + col for col in base_station_df.columns]
        magnetopy_logging.info(f'New station columns: {stations_df.columns}')
        magnetopy_logging.info(f'New base station columns: {base_station_df.columns}')

        return stations_df, base_station_df
    
    @staticmethod
    def save_data(result_df, project_name) -> None:
        """
        Save the resulting dataframe with the calculations performed.

        :param result_df: DataFrame
        :param project_name: str
        :return: Nothing to return
        :rtype: None
        """
        magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetoPyFilesHelper: save_data')
        resources_full_path = os.path.abspath('resources')
        new_folder_path = os.path.join(resources_full_path, project_name)
        os.makedirs(new_folder_path, exist_ok=True)
        magnetopy_logging.info(f'Writing output data on path: {new_folder_path}')
        
        time: str = str(datetime.now()).split('.')[0].replace(' ', '_').replace(':', '')
        file = f'{project_name}_{time}.csv'
        full_path = os.path.abspath(str(os.path.join(new_folder_path, file)))

        result_df.to_csv(full_path)

    @staticmethod
    def most_recent_file(folder_path):
        """
        This function returns the most recent file in the given folder path.
        
        :param folder_path: str
        :return: str
        """
        magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetoPyFilesHelper: most_recent_file')
        pattern = re.compile(r'.*_(\d{4}-\d{2}-\d{2})_(\d{6})\.csv')
        
        most_recent = None
        most_recent_datetime = None
        
        for filename in os.listdir(folder_path):
            match = pattern.match(filename)
            if match:
                file_date_str = match.group(1)
                file_time_str = match.group(2)
                file_datetime_str = f"{file_date_str} {file_time_str}"
                file_datetime = datetime.strptime(file_datetime_str, "%Y-%m-%d %H%M%S")
                
                if most_recent is None or file_datetime > most_recent_datetime:
                    most_recent = filename
                    most_recent_datetime = file_datetime
        
        if most_recent is None:
            raise FileNotFoundError("No matching files found in the specified folder.")
        
        return most_recent
    
    @staticmethod
    def write_igrf_components_to_dataframe(stations_df, igrf_components):
        """
        This function writes the IGRF components to the stations dataframe.

        :param stations_df: pd.DataFrame
        :param igrf_components: dict

        :return: pd.DataFrame
        """
        for col_name, value in igrf_components.items():
            stations_df[col_name] = value

        return stations_df