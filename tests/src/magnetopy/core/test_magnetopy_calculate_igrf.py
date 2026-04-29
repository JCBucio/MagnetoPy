from argparse import Namespace
from logging import getLogger
import os
import unittest

import pandas as pd

from src.magnetopy.magnetopy_core.calculate_igrf import CalculateIGRF
from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper
from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging


class TestCalculateIGRF(unittest.TestCase):
    def test_calculate_igrf(self):
        """
        Test the CalculateIGRF class using the test data in the resources/data_examples folder.

        :return: Nothing to return
        """
        magnetopy_logging = MagnetopyLogging().create_magnetopy_logging(logger='TestCalculateIGRF')

        print("----------------------------------------------------------------------")

        arguments = Namespace(
            project_name='cerritos_test',
            stations_file=os.path.abspath('resources/data_examples/cerritos_datos_estaciones.csv'),
            stations_cols='date,time,gpslat,gpslon,magfield',
            altitude=1.920,
            date='2019-03-26'
        )

        CalculateIGRF(arguments=arguments)

        output_folder = os.path.abspath('resources/cerritos_test')
        output_file = MagnetoPyFilesHelper.most_recent_file(folder_path=output_folder)
        output_file_path = os.path.join(output_folder, output_file)
        expected_output_file = os.path.abspath('resources/data_examples/cerritos_igrf_output.csv')

        output_df = pd.read_csv(output_file_path)
        expected_output_df = pd.read_csv(expected_output_file)

        self.assertTrue(output_df.equals(expected_output_df))

        os.remove(output_file_path)

        magnetopy_logging.info(f'File "{output_file_path}" deleted successfully.')
        magnetopy_logging.info('TestCalculateIGRF: test_calculate_igrf passed successfully.')


if __name__ == '__main__':
    unittest.main()


