#!/usr/bin/env python3
import argparse
from logging import getLogger

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging


class MagnetopyParser:

    def __init__(self):
        self.magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetopyParser')

        self.__magnetopy_parser: argparse.ArgumentParser = argparse.ArgumentParser(
            prog='MagnetoPy', 
            description='MagnetoPy is an open-source tool that performs magnetic data processing.'
            )
        self.__subparsers = self.__magnetopy_parser.add_subparsers(
            title='commands',
            description='magnetopy commands',
            dest='command',
            help='Get help with: <magnetopy_command> --help'
        )

    def __add_diurnal_variation_arguments(self) -> None:
        """
        Add the diurnal-variation command and parameters.

        :return: Nothing to return
        :rtype: None
        """
        diurnal_variation = self.__subparsers.add_parser(
            'diurnal-variation',
            help='MagnetoPy command that calculates the diurnal variation in a dataset.'
        )
        diurnal_variation.add_argument(
            '--stations_file',
            type=str,
            help='Stations file path (required).',
            required=True
        )
        diurnal_variation.add_argument(
            '--stations_cols',
            type=str,
            help='Stations file columns names separated by commas without spaces (required). In the following order: date,time,latitude,longitude,magnetic_field.',
            required=True
        )
        diurnal_variation.add_argument(
            '--base_station_file',
            type=str,
            help='Base station file path (required).',
            required=True
        )
        diurnal_variation.add_argument(
            '--base_station_cols',
            type=str,
            help='Base station file columns names separated by commas (required). In the following order: date,time,magnetic_field.',
            required=True
        )
    
    def __add_calculate_igrf_arguments(self) -> None:
        """
        Add the calculate-igrf command and parameters.

        :return: Nothing to return
        :rtype: None
        """
        calculate_igrf = self.__subparsers.add_parser(
            'calculate-igrf',
            help='Command that performs the IGRF correction to a data set based on the 13th generation coefficients.'
        )
        calculate_igrf.add_argument(
            '--stations_file',
            type=str,
            help='Stations file path (required).',
            required=True
        )
        calculate_igrf.add_argument(
            '--stations_cols',
            type=str,
            help='Stations file columns names separated by commas (required).',
            required=True
        )

    def get_arguments(self) -> argparse.Namespace:
        """
        Gets and returns MagnetoPy commands and parameters.

        :return: Command and its arguments
        :rtype: argparse.Namespace
        """
        self.__add_diurnal_variation_arguments()
        self.__add_calculate_igrf_arguments()

        arguments = self.__magnetopy_parser.parse_args()

        if arguments.command is None:
            self.__magnetopy_parser.print_help()
            exit(1)
        else:
            return arguments