from argparse import Namespace
from logging import getLogger
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper


class PlotProfile:
    def __init__(self, arguments: Namespace):
        self.__magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='PlotProfile')

        self.project_file: str = arguments.project_file
        self.col_to_plot: str | None = getattr(arguments, 'col_to_plot', None)

        self.__plot_profile()

    def __plot_profile(self) -> None:
        """
        Reads the project file and plots the profile of the selected column.

        :return: Nothing to return
        :rtype: None
        """
        self.__magnetopy_logging.info('Reading the project file and plotting the profile')

        _project_file_path = self.project_file

        raw_df = pd.read_csv(_project_file_path, nrows=5)
        if self.col_to_plot:
            _col_to_plot = self.col_to_plot
        else:
            _col_to_plot = MagnetoPyFilesHelper.detect_column(raw_df.columns, 'magnetic_field')
            if not _col_to_plot:
                _col_to_plot = raw_df.columns[-1]
            self.__magnetopy_logging.info(f'Auto-detected column to plot: {_col_to_plot}')

        output_dir = os.path.dirname(os.path.abspath(_project_file_path)) or '.'

        project_df = MagnetoPyFilesHelper.read_and_verify_columns(_project_file_path, [_col_to_plot])

        if project_df is None:
            self.__magnetopy_logging.error('Error reading the project file')
            return
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(pd.to_numeric(project_df[_col_to_plot], errors='coerce'), color='tab:blue', lw=1.5)

        ax.set_xlabel('Station Index')
        ax.set_ylabel(_col_to_plot)
        ax.set_title(f'Profile of column: {_col_to_plot}')
        ax.grid(True, alpha=0.5)

        output_file = os.path.join(output_dir, f'{_col_to_plot}.png')
        fig.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close(fig)

        self.__magnetopy_logging.info(f'Profile plot saved in {output_file}')
        self.__magnetopy_logging.info('Profile plotted successfully')