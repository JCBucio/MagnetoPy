from argparse import Namespace
from logging import getLogger
import pandas as pd

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging

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
        self.__magnetopy_logging.info('Performing the diurnal variation correction')