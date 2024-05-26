"""
Based on code from : chaosmagpy, Clemens Kloss (DTU Space) and pyIGRF, Ciaran Beggan (British Geological Survey)
"""

import os
import pandas as pd
import numpy as np
from math import pi
from datetime import datetime
from logging import getLogger

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging


r2d = np.rad2deg
d2r = np.deg2rad

class IGRF:
    def __init__(self, time, coeffs, parameters):
        self.__magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='IGRF')
        self.time = time
        self.coeffs = coeffs
        self.parameters = parameters

class MagnetoPyIGRFHelper:
    def load_igrf_coefficients(self):
        """
        This function loads the shc-file with the IGRF-13 coefficients and return a IGRF object.

        :return: IGRF object
        """
        magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetoPyIGRFHelper: load_igrf_coefficients')
        magnetopy_logging.info('Loading the IGRF coefficients')
        resources_path = os.path.abspath('resources')
        igrf13_full_path = os.path.join(resources_path, 'igrf13')
        igrf13_file = os.path.join(igrf13_full_path, 'IGRF13.shc')

        if not os.path.exists(igrf13_file):
            raise FileNotFoundError(f"IGRF coefficients file not found: {igrf13_file}")

        with open(igrf13_file, 'r') as f:

            data = np.array([])
            for line in f.readlines():
                if line.startswith('#'):
                    continue

                read_line = np.fromstring(line, sep=' ')
                if read_line.size == 7:
                    name = os.path.split(igrf13_file)[1]
                    values = [name] + read_line.astype(int).tolist()
                else:
                    data = np.append(data, read_line)

        keys = ['SHC', 'nmin', 'nmax', 'N', 'order', 'step', 'start_year', 'end_year']
        parameters = dict(zip(keys, values))

        time = data[:parameters['N']]
        coeffs = data[parameters['N']:].reshape((-1, parameters['N']+2))
        coeffs = np.squeeze(coeffs[:, 2:])

        magnetopy_logging.info(f'IGRF coefficients from file: {igrf13_file} loaded successfully.')

        return IGRF(time, coeffs, parameters)