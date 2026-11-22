from argparse import Namespace
from logging import getLogger
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper
from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging


def _calculate_dynamic_margins(lat_min: float, lat_max: float, lon_min: float, lon_max: float, padding_pct: float = 0.25) -> tuple[float, float]:
    """
    Calculates proportional map margins. Larger areas get larger padding,
    while extremely small areas default to a high-zoom minimum.
    """
    lat_spread = lat_max - lat_min
    lon_spread = lon_max - lon_min

    # 0.00005 degrees is roughly 5.5 meters
    absolute_min_margin = 0.00005

    lat_margin = absolute_min_margin if lat_spread == 0 else max(absolute_min_margin, lat_spread * padding_pct)
    lon_margin = absolute_min_margin if lon_spread == 0 else max(absolute_min_margin, lon_spread * padding_pct)

    return lat_margin, lon_margin


def run_plot_map(arguments: Namespace) -> None:
    """
    Reads the project file and plots the geographic location of the points
    using pure matplotlib (no cartopy dependency).
    The figure is saved as a PNG next to the input file.

    :param arguments: Parsed CLI namespace
    :return: None
    """
    log: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='PlotMap')
    log.info('Reading the project file and plotting the geographic points')

    _project_file_path = arguments.project_file
    latitude_col_arg = getattr(arguments, 'latitude_col', None)
    longitude_col_arg = getattr(arguments, 'longitude_col', None)

    raw_df = pd.read_csv(_project_file_path, nrows=5)
    if latitude_col_arg:
        _latitude_col = latitude_col_arg
    else:
        _latitude_col = MagnetoPyFilesHelper.detect_column(raw_df.columns, 'latitude')
        if not _latitude_col:
            raise ValueError(f"Could not auto-detect latitude column from headers: {list(raw_df.columns)}. Specify --latitude_col.")
        log.info(f'Auto-detected latitude column: {_latitude_col}')

    if longitude_col_arg:
        _longitude_col = longitude_col_arg
    else:
        _longitude_col = MagnetoPyFilesHelper.detect_column(raw_df.columns, 'longitude')
        if not _longitude_col:
            raise ValueError(f"Could not auto-detect longitude column from headers: {list(raw_df.columns)}. Specify --longitude_col.")
        log.info(f'Auto-detected longitude column: {_longitude_col}')

    project_df = MagnetoPyFilesHelper.read_and_verify_columns(_project_file_path, [_latitude_col, _longitude_col])
    if project_df is None:
        log.error('Error reading the project file')
        return

    try:
        project_df[_latitude_col] = pd.to_numeric(project_df[_latitude_col], errors='raise')
        project_df[_longitude_col] = pd.to_numeric(project_df[_longitude_col], errors='raise')
    except ValueError as exc:
        log.error(f'Invalid numeric values in the latitude/longitude columns: {exc}')
        return

    for latitude in project_df[_latitude_col]:
        MagnetoPyFilesHelper.check_lat_bounds(float(latitude))

    for longitude in project_df[_longitude_col]:
        MagnetoPyFilesHelper.check_lon_bounds(float(longitude))

    lat_min = float(project_df[_latitude_col].min())
    lat_max = float(project_df[_latitude_col].max())
    lon_min = float(project_df[_longitude_col].min())
    lon_max = float(project_df[_longitude_col].max())

    lat_margin, lon_margin = _calculate_dynamic_margins(lat_min, lat_max, lon_min, lon_max)

    # Clamp extents so they don't exceed physical geographic boundaries
    ext_lon_min = max(-180.0, lon_min - lon_margin)
    ext_lon_max = min(180.0, lon_max + lon_margin)
    ext_lat_min = max(-90.0, lat_min - lat_margin)
    ext_lat_max = min(90.0, lat_max + lat_margin)

    fig, ax = plt.subplots(figsize=(10, 8))

    ax.scatter(
        project_df[_longitude_col],
        project_df[_latitude_col],
        s=50, c='tab:blue', edgecolors='black', zorder=5
    )

    ax.set_xlim(ext_lon_min, ext_lon_max)
    ax.set_ylim(ext_lat_min, ext_lat_max)

    # Approximate equal-area aspect ratio: 1 degree longitude ≈ cos(lat) degrees latitude
    lat_avg = (lat_min + lat_max) / 2.0
    ax.set_aspect(1 / np.cos(np.radians(lat_avg)))

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Magnetic data points by location')
    ax.grid(color='gray', alpha=0.5, linestyle='--')

    output_dir = os.path.dirname(os.path.abspath(_project_file_path))
    output_file = os.path.join(output_dir, f'{os.path.splitext(os.path.basename(_project_file_path))[0]}_map.png')

    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)

    log.info(f'Map saved in {output_file}')
    log.info('Map plotted successfully')
