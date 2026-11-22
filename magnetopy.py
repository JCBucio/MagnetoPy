#!/usr/bin/env python3
from logging import getLogger
from argparse import Namespace

from src.magnetopy.magnetopy_core.diurnal_variation import run_diurnal_variation
from src.magnetopy.magnetopy_core.calculate_igrf import run_calculate_igrf
from src.magnetopy.magnetopy_core.plot_profile import run_plot_profile
from src.magnetopy.magnetopy_core.plot_map import run_plot_map
from src.magnetopy.magnetopy_core.reduction_to_pole import run_reduction_to_pole
from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
from src.magnetopy.magnetopy_cli.magnetopy_parser import MagnetopyParser


_COMMANDS = {
    'diurnal-variation': run_diurnal_variation,
    'calculate-igrf':    run_calculate_igrf,
    'plot-profile':      run_plot_profile,
    'plot-map':          run_plot_map,
    'reduction-to-pole': run_reduction_to_pole,
}


def _print_banner(log: getLogger, arguments: Namespace) -> None:
    arguments_str = ''.join(f'{k}: {v}\n' for k, v in vars(arguments).items())
    banner = f'''
######################## MAGNETOPY ########################
##                                                       ##  
##  Written by Juan Carlos Bucio (jcbucio.geo@gmail.com) ##
##     Universidad Nacional Autónoma de México (UNAM)    ##
##                                                       ##
##   Supervised by M.Sc. Dulce María Gutiérrez Carmona   ##
##            and Dr. Gerardo Cifuentes Nava             ##
##                                                       ##
##               Licensed under MIT license              ##
##                                                       ##
###########################################################

{arguments_str}
###########################################################
    '''
    log.info(banner)


def main() -> None:
    log: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetoPy')

    parser = MagnetopyParser()
    arguments: Namespace = parser.get_arguments()
    command: str = arguments.command

    _print_banner(log, arguments)

    runner = _COMMANDS.get(command)
    if runner is None:
        log.error(f"Unknown command: '{command}'")
        return

    log.info(f"{command} command selected")
    runner(arguments)


if __name__ == '__main__':
    main()
