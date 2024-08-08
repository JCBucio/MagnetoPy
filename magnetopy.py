#!/usr/bin/env python3
from logging import getLogger
from argparse import Namespace

from src.magnetopy.magnetopy_core.diurnal_variation import DiurnalVariation
from src.magnetopy.magnetopy_core.calculate_igrf import CalculateIGRF
from src.magnetopy.magnetopy_core.plot_profile import PlotProfile
from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
from src.magnetopy.magnetopy_cli.magnetopy_parser import MagnetopyParser


class Magnetopy:
    
    def __init__(self):
        self.magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetoPy')

        self.__parser: MagnetopyParser = MagnetopyParser()
        self.__arguments: Namespace = self.__parser.get_arguments()
        self.command: str = self.__arguments.command

        self.__magnetopy_flow()

    def __magnetopy_flow(self) -> None:
        """
        Runs the MagnetoPy validation flow depending on the command.

        :return: Nothing to return
        :rtype: None
        """
        self.__print_banner()

        if self.command == 'diurnal-variation':
            self.magnetopy_logging.info("diurnal-variation command selected")
            DiurnalVariation(arguments=self.__arguments)
        elif self.command == 'calculate-igrf':
            self.magnetopy_logging.info("calculate-igrf command selected")
            CalculateIGRF(arguments=self.__arguments)
        elif self.command == 'plot-profile':
            self.magnetopy_logging.info("plot-profile command selected")
            PlotProfile(arguments=self.__arguments)

    def __print_banner(self) -> None:
        """
        Print banner

        :return: Nothing to return
        :rtype: None
        """
        arguments_str = ''
        for argument_name, argument_value in vars(self.__arguments).items():
            arguments_str += f'{argument_name}: {argument_value}\n'

        banner = f'''
######################## MAGNETOPY ########################
##                                                       ##  
##  Written by Juan Carlos Bucio (jcbucio.geo@gmail.com) ##
##               Licensed under MIT license              ##
##                                                       ##
###########################################################

{arguments_str}
###########################################################
        '''

        self.magnetopy_logging.info(banner)

if __name__ == '__main__':
    Magnetopy()