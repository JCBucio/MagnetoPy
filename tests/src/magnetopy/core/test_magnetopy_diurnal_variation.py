from argparse import Namespace
from logging import getLogger

import os
import unittest
import pandas as pd

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper
from src.magnetopy.magnetopy_core.diurnal_variation import DiurnalVariation


class TestDiurnalVariation(unittest.TestCase):
    def test_diurnal_variation(self):
        """
        Test the DiurnalVariation class using the test data in the resources/data_examples folder.

        :return: Nothing to return
        """
        magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='TestDiurnalVariation')

        arguments = Namespace(
            project_name='cerritos',
            stations_file=os.path.abspath('resources/data_examples/cerritos_datos_estaciones.csv'),
            stations_cols='date,time,gpslat,gpslon,magfield',
            base_station_file=os.path.abspath('resources/data_examples/cerritos_estaciones_base.csv'),
            base_station_cols='date,time,nT'
        )

        DiurnalVariation(arguments=arguments)

        output_folder = os.path.abspath('resources/cerritos')
        output_file = MagnetoPyFilesHelper.most_recent_file(folder_path=output_folder)
        output_file_path = os.path.join(output_folder, output_file)
        expected_output_file = os.path.abspath('resources/data_examples/cerritos_output.csv')

        output_df = pd.read_csv(output_file_path)
        expected_output_df = pd.read_csv(expected_output_file)

        self.assertTrue(output_df.equals(expected_output_df))

        os.remove(output_file_path)

        magnetopy_logging.info(f'File "{output_file_path}" deleted successfully.')
        magnetopy_logging.info('TestDiurnalVariation: test_diurnal_variation passed successfully.')

if __name__ == '__main__':
    unittest.main()