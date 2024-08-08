from argparse import Namespace
from logging import getLogger
import pandas as pd
import matplotlib.pyplot as plt

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper


class PlotProfile:
    def __init__(self, arguments: Namespace):
        self.__magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='PlotProfile')

        self.project_file: str = arguments.project_file
        self.col_to_plot: str = arguments.col_to_plot

        self.__plot_profile()

    def __plot_profile(self) -> None:
        """
        Reads the project file and plots the profile of the selected column.

        :return: Nothing to return
        :rtype: None
        """
        self.__magnetopy_logging.info('Reading the project file and plotting the profile')

        _project_file_path = self.project_file
        _col_to_plot = self.col_to_plot

        project_df = MagnetoPyFilesHelper.read_and_verify_columns(_project_file_path, [_col_to_plot])

        if project_df is None:
            self.__magnetopy_logging.error('Error reading the project file')
            return
        
        plt.plot(project_df[_col_to_plot])

        plt.xlabel('Index')
        plt.ylabel(_col_to_plot)
        plt.title(f'Profile of the column: {_col_to_plot}')
        plt.grid(alpha=0.5)

        plt.show(block=True)

        self.__magnetopy_logging.info('Profile plotted successfully')