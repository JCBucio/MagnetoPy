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

        print("----------------------------------------------------------------------")

        arguments = Namespace(
            project_name='cerritos_test',
            stations_file=os.path.abspath('resources/data_examples/cerritos_datos_estaciones.csv'),
            stations_cols='date,time,gpslat,gpslon,magfield',
            base_station_file=os.path.abspath('resources/data_examples/cerritos_estaciones_base.csv'),
            base_station_cols='date,time,nT'
        )

        DiurnalVariation(arguments=arguments)

        output_folder = os.path.abspath('resources/cerritos_test')
        output_file = MagnetoPyFilesHelper.most_recent_file(folder_path=output_folder)
        output_file_path = os.path.join(output_folder, output_file)
        output_df = pd.read_csv(output_file_path)

        expected_columns = [
            'sta_date', 'sta_time', 'sta_gpslat', 'sta_gpslon', 'sta_magfield',
            'sta_datetime', 'base_date', 'base_time', 'base_nT', 'base_datetime',
            'base_magfield_mean', 'time_diff', 'diurnal_var', 'diurnal_var_corr'
        ]
        for col in expected_columns:
            self.assertIn(col, output_df.columns)

        input_stations_df = pd.read_csv(arguments.stations_file)
        self.assertEqual(len(output_df), len(input_stations_df))

        # Check mathematical relationships:
        # diurnal_var == base_nT - base_magfield_mean
        expected_diurnal_var = output_df['base_nT'] - output_df['base_magfield_mean']
        self.assertTrue((abs(output_df['diurnal_var'] - expected_diurnal_var) < 1e-4).all())

        # diurnal_var_corr == sta_magfield - diurnal_var
        expected_corr = output_df['sta_magfield'] - output_df['diurnal_var']
        self.assertTrue((abs(output_df['diurnal_var_corr'] - expected_corr) < 1e-4).all())

        os.remove(output_file_path)

        magnetopy_logging.info(f'File "{output_file_path}" deleted successfully.')
        magnetopy_logging.info('TestDiurnalVariation: test_diurnal_variation passed successfully.')

    def test_diurnal_variation_auto_detection(self):
        """
        Test diurnal variation using column auto-detection (no explicit column flags or project name).
        """
        arguments = Namespace(
            project_name=None,
            stations_file=os.path.abspath('resources/data_examples/cerritos_datos_estaciones.csv'),
            stations_cols=None,
            base_station_file=os.path.abspath('resources/data_examples/cerritos_estaciones_base.csv'),
            base_station_cols=None
        )

        DiurnalVariation(arguments=arguments)

        output_folder = os.path.abspath('resources/cerritos_datos_estaciones')
        output_file = MagnetoPyFilesHelper.most_recent_file(folder_path=output_folder)
        output_file_path = os.path.join(output_folder, output_file)

        output_df = pd.read_csv(output_file_path)

        self.assertIn('diurnal_var_corr', output_df.columns)
        input_stations_df = pd.read_csv(arguments.stations_file)
        self.assertEqual(len(output_df), len(input_stations_df))

        os.remove(output_file_path)

if __name__ == '__main__':
    unittest.main()