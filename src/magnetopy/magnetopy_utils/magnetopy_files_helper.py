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
