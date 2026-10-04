#!/usr/bin/env python3
import argparse
import configparser
import json
import os
from logging import getLogger

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging


class MagnetopyParser:

    def __init__(self):
        self.magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetopyParser')

        self.__magnetopy_parser: argparse.ArgumentParser = argparse.ArgumentParser(
            prog='MagnetoPy', 
            description='MagnetoPy is an open-source tool that performs magnetic data processing.'
            )
        self.__add_config_argument(self.__magnetopy_parser)
        self.__subparsers = self.__magnetopy_parser.add_subparsers(
            title='commands',
            description='magnetopy commands',
            dest='command',
            help='Get help with: <magnetopy_command> --help'
        )

    @staticmethod
    def __normalize_config_key(key: str) -> str:
        return key.strip().replace('-', '_')

    @staticmethod
    def __add_config_argument(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--config',
            type=str,
            help='Optional config file path (JSON, YAML/YML, or INI). CLI arguments override values from the config file.'
        )

    def __load_config_file(self, config_path: str) -> dict:
        """
        Loads a configuration file into a dictionary, supporting JSON, YAML/YML, and INI formats.
        """
        if not config_path:
            return {}

        absolute_path = os.path.abspath(config_path)
        if not os.path.exists(absolute_path):
            raise FileNotFoundError(f'Config file not found: {absolute_path}')

        extension = os.path.splitext(absolute_path)[1].lower()

        if extension == '.json':
            with open(absolute_path, 'r', encoding='utf-8') as config_file:
                data = json.load(config_file)
            if not isinstance(data, dict):
                raise ValueError('The JSON config file must contain an object at the root.')
            return data

        if extension in {'.yaml', '.yml'}:
            try:
                import yaml
            except ImportError as exc:
                raise RuntimeError(
                    'YAML config support requires PyYAML to be installed. Install it with "pip install pyyaml".'
                ) from exc
            with open(absolute_path, 'r', encoding='utf-8') as config_file:
                data = yaml.safe_load(config_file)
            if data is None:
                return {}
            if not isinstance(data, dict):
                raise ValueError('The YAML config file must contain a dictionary at the root.')
            return data

        if extension in {'.ini', '.cfg'}:
            config = configparser.ConfigParser()
            config.read(absolute_path)
            values = {}
            for section in config.sections():
                for key, value in config.items(section):
                    values[self.__normalize_config_key(key)] = value
            return values

        raise ValueError(
            'Unsupported config format. Use a .json, .yaml/.yml, or .ini/.cfg file.'
        )

    def __merge_config_into_arguments(self, arguments: argparse.Namespace) -> argparse.Namespace:
        """
        Merges values from the config file into the parsed arguments. CLI values remain authoritative.
        """
        config_path = getattr(arguments, 'config', None)
        if not config_path:
            return arguments

        config_data = self.__load_config_file(config_path)

        if not isinstance(config_data, dict):
            raise ValueError('Configuration content must be a dictionary keyed by argument names.')

        command_name = getattr(arguments, 'command', None)
        command_section = None
        if command_name is not None:
            command_section = config_data.get(command_name)
            if isinstance(command_section, dict):
                config_data = {**config_data, **command_section}

        normalized_config = {}
        for key, value in config_data.items():
            normalized_key = self.__normalize_config_key(str(key))
            normalized_config[normalized_key] = value

        for key, value in normalized_config.items():
            if not hasattr(arguments, key):
                continue
            if getattr(arguments, key) is None:
                setattr(arguments, key, value)

        return arguments

    def __validate_required_arguments(self, arguments: argparse.Namespace) -> None:
        required_by_command = {
            'diurnal-variation': ['project_name', 'stations_file', 'stations_cols', 'base_station_file', 'base_station_cols'],
            'calculate-igrf': ['project_name', 'stations_file', 'stations_cols', 'altitude', 'date'],
            'plot-profile': ['project_file', 'col_to_plot'],
            'plot-map': ['project_file', 'latitude_col', 'longitude_col'],
            'reduction-to-pole': ['project_name', 'project_file', 'easting_col', 'northing_col', 'magnetic_field_col', 'inclination', 'declination'],
        }

        command_name = getattr(arguments, 'command', None)
        if command_name is None:
            return

        required_args = required_by_command.get(command_name, [])
        missing_args = []
        for arg_name in required_args:
            value = getattr(arguments, arg_name, None)
            if value is None or value == '':
                missing_args.append(f'--{arg_name.replace("_", "-")}')

        if missing_args:
            raise ValueError(
                f"Missing required arguments for '{command_name}': {', '.join(missing_args)}. "
                "Pass them directly on the CLI or provide them in the config file."
            )

    def __add_diurnal_variation_arguments(self) -> None:
        """
        Add the diurnal-variation command and parameters.

        :return: Nothing to return
        :rtype: None
        """
        diurnal_variation = self.__subparsers.add_parser(
            'diurnal-variation',
            help='MagnetoPy command that calculates the diurnal variation in a dataset.',
            description='MagnetoPy command that calculates the diurnal variation in a dataset. It requires a stations file and a base station file to perform the calculations.'
        )
        self.__add_config_argument(diurnal_variation)
        diurnal_variation.add_argument(
            '--project_name',
            '-p',
            type=str,
            help='Project name (without spaces or special characters) to name the folder where the output will be saved (required).',
            default=None
        )
        diurnal_variation.add_argument(
            '--stations_file',
            '-s',
            type=str,
            help='Stations file path (required).',
            default=None
        )
        diurnal_variation.add_argument(
            '--stations_cols',
            '-c',
            type=str,
            help='Stations file columns names separated by commas without spaces (required). In the following order: date,time,latitude,longitude,magnetic_field.',
            default=None
        )
        diurnal_variation.add_argument(
            '--base_station_file',
            '-b',
            type=str,
            help='Base station file path (required).',
            default=None
        )
        diurnal_variation.add_argument(
            '--base_station_cols',
            '-B',
            type=str,
            help='Base station file columns names separated by commas (required). In the following order: date,time,magnetic_field.',
            default=None
        )
    
    def __add_calculate_igrf_arguments(self) -> None:
        """
        Add the calculate-igrf command and parameters.

        :return: Nothing to return
        :rtype: None
        """
        calculate_igrf = self.__subparsers.add_parser(
            'calculate-igrf',
            help='Command that performs the IGRF-14 correction to a data set based on the 14th generation coefficients.',
            description='Command that performs the IGRF-14 correction to a data set based on the 14th generation coefficients.'
        )
        self.__add_config_argument(calculate_igrf)
        calculate_igrf.add_argument(
            '--project_name',
            '-p',
            type=str,
            help='Project name (without spaces or special characters) to name the folder where the output will be saved (required).',
            default=None
        )
        calculate_igrf.add_argument(
            '--stations_file',
            '-s',
            type=str,
            help='Stations file path (required).',
            default=None
        )
        calculate_igrf.add_argument(
            '--stations_cols',
            '-c',
            type=str,
            help='Stations file columns in the following order: date, time, magfield, latitude and longitude (required).',
            default=None
        )
        calculate_igrf.add_argument(
            '--altitude',
            '-a',
            type=float,
            help='Altitude in km (required).',
            default=None
        )
        calculate_igrf.add_argument(
            '--date',
            '-d',
            type=str,
            help='Date in format YYYY-MM-DD (required).',
            default=None
        )
        calculate_igrf.add_argument(
            '--verbose',
            action='store_true',
            help='Include the secular variation columns in the output CSV. By default only the main IGRF components are included.'
        )

    def __add_plot_profile_arguments(self) -> None:
        """
        Add the plot-profile command and parameters.

        :return: Nothing to return
        :rtype: None
        """
        plot_profile = self.__subparsers.add_parser(
            'plot-profile',
            help='Command that reads the project file and plots the profile of the selected column.',
            description='Command that reads the project file and plots the profile of the selected column.'
        )
        self.__add_config_argument(plot_profile)
        plot_profile.add_argument(
            '--project_file',
            '-f',
            type=str,
            help='Project file path (required).',
            default=None
        )
        plot_profile.add_argument(
            '--col_to_plot',
            '-C',
            type=str,
            help='Column to plot (required).',
            default=None
        )

    def __add_plot_map_arguments(self) -> None:
        """
        Add the plot-map command and parameters.

        :return: Nothing to return
        :rtype: None
        """
        plot_map = self.__subparsers.add_parser(
            'plot-map',
            help='Command that reads the data file and plots the points on a geographic map.',
            description='Command that reads the data file and plots the points on a geographic map.'
        )
        self.__add_config_argument(plot_map)
        plot_map.add_argument(
            '--project_file',
            '-f',
            type=str,
            help='Project CSV file path (required).',
            default=None
        )
        plot_map.add_argument(
            '--latitude_col',
            '-lat',
            type=str,
            help='Latitude column name in the CSV file (required).',
            default=None
        )
        plot_map.add_argument(
            '--longitude_col',
            '-lon',
            type=str,
            help='Longitude column name in the CSV file (required).',
            default=None
        )

    def __add_reduction_to_pole_arguments(self) -> None:
        """
        Add the reduction-to-pole command and parameters.

        :return: Nothing to return
        :rtype: None
        """
        reduction_to_pole = self.__subparsers.add_parser(
            'reduction-to-pole',
            help='Command that computes a reduction-to-pole magnetic grid using Harmonica.',
            description='Command that computes a reduction-to-pole magnetic grid using Harmonica.'
        )
        self.__add_config_argument(reduction_to_pole)
        reduction_to_pole.add_argument(
            '--project_name',
            '-p',
            type=str,
            help='Project name (without spaces or special characters) to name the folder where the output will be saved (required).',
            default=None
        )
        reduction_to_pole.add_argument(
            '--project_file',
            '-f',
            type=str,
            help='Project CSV file path containing a regular magnetic grid. Expected columns: easting, northing and magnetic_field (required).',
            default=None
        )
        reduction_to_pole.add_argument(
            '--easting_col',
            '-e',
            type=str,
            help='Easting coordinate column name in the CSV file (required).',
            default=None
        )
        reduction_to_pole.add_argument(
            '--northing_col',
            '-n',
            type=str,
            help='Northing coordinate column name in the CSV file (required).',
            default=None
        )
        reduction_to_pole.add_argument(
            '--magnetic_field_col',
            '-m',
            type=str,
            help='Magnetic field values column name in the CSV file (required).',
            default=None
        )
        reduction_to_pole.add_argument(
            '--inclination',
            '-i',
            type=float,
            help='Inclination of the inducing geomagnetic field in degrees (required).',
            default=None
        )
        reduction_to_pole.add_argument(
            '--declination',
            '-D',
            type=float,
            help='Declination of the inducing geomagnetic field in degrees (required).',
            default=None
        )
        reduction_to_pole.add_argument(
            '--magnetization_inclination',
            type=float,
            help='Optional magnetization inclination in degrees. Defaults to the inducing field inclination.',
            default=None
        )
        reduction_to_pole.add_argument(
            '--magnetization_declination',
            type=float,
            help='Optional magnetization declination in degrees. Defaults to the inducing field declination.',
            default=None
        )
        reduction_to_pole.add_argument(
            '--upward_col',
            type=str,
            help='Optional altitude/upward coordinate column. Used when the observation height varies significantly, especially with equivalent-sources approximation.',
            default=None
        )
        reduction_to_pole.add_argument(
            '--equivalent-sources',
            action='store_true',
            help='Use the Harmonica equivalent-sources approximation instead of the default Verde spline interpolation. This is particularly useful when the data have strong altitude variations, such as in aeromagnetic surveys.'
        )

    def get_arguments(self) -> argparse.Namespace:
        """
        Gets and returns MagnetoPy commands and parameters.

        :return: Command and its arguments
        :rtype: argparse.Namespace
        """
        self.__add_diurnal_variation_arguments()
        self.__add_calculate_igrf_arguments()
        self.__add_plot_profile_arguments()
        self.__add_plot_map_arguments()
        self.__add_reduction_to_pole_arguments()

        arguments = self.__magnetopy_parser.parse_args()

        if arguments.command is None:
            self.__magnetopy_parser.print_help()
            exit(1)

        arguments = self.__merge_config_into_arguments(arguments)
        self.__validate_required_arguments(arguments)

        return arguments