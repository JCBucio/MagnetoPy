from argparse import Namespace
from logging import getLogger
import pandas as pd

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper

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

        igrf_df = MagnetoPyFilesHelper.load_igrf_coefficients()

        # Show the first 5 rows of the IGRF coefficients
        self.__magnetopy_logging.info(f'First 5 rows of the IGRF coefficients:\n{igrf_df.head()}')

        # Show columns of the IGRF coefficients
        self.__magnetopy_logging.info(f'IGRF coefficients columns:\n{igrf_df.columns}')

        return None