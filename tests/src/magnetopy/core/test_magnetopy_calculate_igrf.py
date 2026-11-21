from argparse import Namespace
from logging import getLogger
import os
import unittest

import pandas as pd

from src.magnetopy.magnetopy_core.calculate_igrf import CalculateIGRF
from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper
from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging


class TestCalculateIGRF(unittest.TestCase):
    def test_calculate_igrf_default_output(self):
        """
        Test the default CalculateIGRF output using the test data in the resources/data_examples folder.

        :return: Nothing to return
        """
        magnetopy_logging = MagnetopyLogging().create_magnetopy_logging(logger='TestCalculateIGRF')

        arguments = Namespace(
            project_name='cerritos_test',
            stations_file=os.path.abspath('resources/data_examples/cerritos_datos_estaciones.csv'),
            stations_cols='date,time,gpslat,gpslon,magfield',
            altitude=1.920,
            date='2019-03-26',
            verbose=False,
        )

        CalculateIGRF(arguments=arguments)

        output_folder = os.path.abspath('resources/cerritos_test')
        output_file = MagnetoPyFilesHelper.most_recent_file(folder_path=output_folder)
        output_file_path = os.path.join(output_folder, output_file)

        output_df = pd.read_csv(output_file_path)

        for col in ['D(°)', 'I(°)', 'H(nT)', 'F(nT)', 'X(nT)', 'Y(nT)', 'Z(nT)', 'mag_anomaly(nT)']:
            self.assertIn(col, output_df.columns)
        self.assertNotIn('SV_D(min/yr)', output_df.columns)
        self.assertNotIn('B_radius', output_df.columns)

        # Verify that mag_anomaly(nT) equals observed magfield minus IGRF F(nT)
        expected_anomaly = output_df['magfield'] - output_df['F(nT)']
        self.assertTrue((abs(output_df['mag_anomaly(nT)'] - expected_anomaly) < 1e-4).all())

        os.remove(output_file_path)

        magnetopy_logging.info(f'File "{output_file_path}" deleted successfully.')
        magnetopy_logging.info('TestCalculateIGRF: test_calculate_igrf_default_output passed successfully.')

    def test_calculate_igrf_verbose_output(self):
        """
        Test the verbose CalculateIGRF output includes the secular variation columns and input data columns.
        """
        arguments = Namespace(
            project_name='cerritos_test_verbose',
            stations_file=os.path.abspath('resources/data_examples/cerritos_datos_estaciones.csv'),
            stations_cols='date,time,gpslat,gpslon,magfield',
            altitude=1.920,
            date='2019-03-26',
            verbose=True,
        )

        CalculateIGRF(arguments=arguments)

        output_folder = os.path.abspath('resources/cerritos_test_verbose')
        output_file = MagnetoPyFilesHelper.most_recent_file(folder_path=output_folder)
        output_file_path = os.path.join(output_folder, output_file)
        output_df = pd.read_csv(output_file_path)

        required_input_cols = ['date', 'time', 'gpslat', 'gpslon', 'magfield']
        for col in required_input_cols:
            self.assertIn(col, output_df.columns)

        for col in ['D(°)', 'I(°)', 'H(nT)', 'F(nT)', 'X(nT)', 'Y(nT)', 'Z(nT)', 'mag_anomaly(nT)']:
            self.assertIn(col, output_df.columns)

        for col in ['SV_D(min/yr)', 'SV_I(min/yr)', 'SV_H(nT/yr)', 'SV_F(nT/yr)', 'SV_X(nT/yr)', 'SV_Y(nT/yr)', 'SV_Z(nT/yr)']:
            self.assertIn(col, output_df.columns)

        self.assertNotIn('B_radius', output_df.columns)
        self.assertNotIn('B_theta', output_df.columns)
        self.assertNotIn('B_phi', output_df.columns)

        # Verify that mag_anomaly(nT) equals observed magfield minus IGRF F(nT)
        expected_anomaly = output_df['magfield'] - output_df['F(nT)']
        self.assertTrue((abs(output_df['mag_anomaly(nT)'] - expected_anomaly) < 1e-4).all())

        os.remove(output_file_path)

    def test_calculate_igrf_auto_detection(self):
        """
        Test calculate-igrf using auto-detection for date, columns, and project_name.
        """
        arguments = Namespace(
            project_name=None,
            stations_file=os.path.abspath('resources/data_examples/cerritos_datos_estaciones.csv'),
            stations_cols=None,
            altitude=1.920,
            date=None,
            verbose=False,
        )

        CalculateIGRF(arguments=arguments)

        output_folder = os.path.abspath('resources/cerritos_datos_estaciones')
        output_file = MagnetoPyFilesHelper.most_recent_file(folder_path=output_folder)
        output_file_path = os.path.join(output_folder, output_file)
        output_df = pd.read_csv(output_file_path)

        self.assertIn('mag_anomaly(nT)', output_df.columns)
        self.assertIn('F(nT)', output_df.columns)
        self.assertEqual(len(output_df), 44)

        os.remove(output_file_path)


if __name__ == '__main__':
    unittest.main()
