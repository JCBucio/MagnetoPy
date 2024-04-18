from argparse import Namespace
from logging import getLogger
import pandas as pd

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging

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

        self.__magnetopy_logging.info(f'Stations file path: {str(_stations_file_path)}')
        self.__magnetopy_logging.info(f'Stations columns: {str(_stations_cols)}')