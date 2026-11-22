from argparse import Namespace
from logging import getLogger
import os

import numpy as np
import pandas as pd
import xarray as xr
import harmonica
import verde

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper


def _is_regular_grid(df: pd.DataFrame, easting_col: str, northing_col: str) -> bool:
    """
    Check whether the data already form a regular grid with constant spacing in both axes.
    """
    x_values = pd.to_numeric(df[easting_col], errors='coerce').dropna().drop_duplicates().sort_values().to_numpy()
    y_values = pd.to_numeric(df[northing_col], errors='coerce').dropna().drop_duplicates().sort_values().to_numpy()

    if len(x_values) < 2 or len(y_values) < 2:
        return False

    x_step = np.diff(x_values)
    y_step = np.diff(y_values)

    if np.any(x_step <= 0) or np.any(y_step <= 0):
        return False

    return np.allclose(x_step, x_step[0], rtol=1e-5, atol=1e-8) and np.allclose(y_step, y_step[0], rtol=1e-5, atol=1e-8)


def _prepare_regular_grid(df: pd.DataFrame, easting_col: str, northing_col: str, magnetic_field_col: str) -> xr.DataArray:
    """
    Convert the tabular CSV grid to an xarray DataArray used by Harmonica.
    """
    grid_df = df[[easting_col, northing_col, magnetic_field_col]].copy()
    grid_df[easting_col] = pd.to_numeric(grid_df[easting_col], errors='raise')
    grid_df[northing_col] = pd.to_numeric(grid_df[northing_col], errors='raise')
    grid_df[magnetic_field_col] = pd.to_numeric(grid_df[magnetic_field_col], errors='raise')

    x = pd.Index(grid_df[easting_col].drop_duplicates().sort_values(), name=easting_col)
    y = pd.Index(grid_df[northing_col].drop_duplicates().sort_values(), name=northing_col)

    data = grid_df.pivot(index=northing_col, columns=easting_col, values=magnetic_field_col)
    data = data.reindex(index=y, columns=x)

    return xr.DataArray(
        data.to_numpy(),
        coords={'northing': y, 'easting': x},
        dims=('northing', 'easting'),
        name=magnetic_field_col,
    )


def _interpolate_to_regular_grid(df: pd.DataFrame, easting_col: str, northing_col: str, magnetic_field_col: str, upward_col: str | None) -> xr.DataArray:
    """
    Interpolate irregular data onto a regular grid with Verde spline interpolation.
    The default behavior is a regularized spline, which is robust for most survey data.
    """
    easting = pd.to_numeric(df[easting_col], errors='raise')
    northing = pd.to_numeric(df[northing_col], errors='raise')
    data = pd.to_numeric(df[magnetic_field_col], errors='raise')

    region = [easting.min(), easting.max(), northing.min(), northing.max()]
    spacing = (
        np.median(np.diff(np.sort(np.unique(northing)))),
        np.median(np.diff(np.sort(np.unique(easting)))),
    )

    spline = verde.Spline()
    if upward_col is not None:
        upward = pd.to_numeric(df[upward_col], errors='raise')
        grid_coords = verde.grid_coordinates(region=region, spacing=spacing, extra_coords={'upward': np.mean(upward)})
        interpolated = spline.fit((easting, northing, upward), data)
        grid = interpolated.grid(coordinates=grid_coords, data_names='magnetic_field')
    else:
        interpolated = spline.fit((easting, northing), data)
        grid = interpolated.grid(region=region, spacing=spacing, data_names='magnetic_field')

    return grid['magnetic_field']


def _equivalent_sources_grid(df: pd.DataFrame, easting_col: str, northing_col: str, magnetic_field_col: str, upward_col: str | None) -> xr.DataArray:
    """
    Approximate irregular data using Harmonica equivalent sources.
    Especially useful when the data have significant height variation (e.g., aeromagnetic surveys).
    """
    easting = pd.to_numeric(df[easting_col], errors='raise').to_numpy()
    northing = pd.to_numeric(df[northing_col], errors='raise').to_numpy()
    magnetic = pd.to_numeric(df[magnetic_field_col], errors='raise').to_numpy()
    upward = pd.to_numeric(df[upward_col], errors='raise').to_numpy() if upward_col is not None else np.zeros_like(easting, dtype=float)

    region = [easting.min(), easting.max(), northing.min(), northing.max()]
    grid_coords = verde.grid_coordinates(
        region=region,
        spacing=(np.median(np.diff(np.sort(np.unique(northing)))), np.median(np.diff(np.sort(np.unique(easting))))),
        extra_coords={'upward': 0}
    )

    eq = harmonica.EquivalentSources(depth='default')
    fitted = eq.fit((easting, northing, upward), magnetic)
    grid = fitted.grid(coordinates=(grid_coords[0], grid_coords[1], grid_coords[2]), data_names='magnetic_field')

    return grid['magnetic_field']


def run_reduction_to_pole(arguments: Namespace) -> None:
    """
    Performs a reduction-to-pole transformation using Harmonica.
    If the input is irregular, it is first gridded using the default Verde spline
    interpolation, or approximated with equivalent sources when requested.

    :param arguments: Parsed CLI namespace
    :return: None
    """
    log: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='ReductionToPole')
    log.info('Validating the project grid and preparing the RTP input')

    _project_file_path = arguments.project_file
    _project_name = getattr(arguments, 'project_name', None) or os.path.splitext(os.path.basename(_project_file_path))[0]
    inclination = arguments.inclination
    declination = arguments.declination
    magnetization_inclination = getattr(arguments, 'magnetization_inclination', None) or inclination
    magnetization_declination = getattr(arguments, 'magnetization_declination', None) or declination
    upward_col = getattr(arguments, 'upward_col', None)
    use_equivalent_sources = getattr(arguments, 'equivalent_sources', False)

    raw_df = pd.read_csv(_project_file_path, nrows=5)

    easting_col = getattr(arguments, 'easting_col', None)
    if not easting_col:
        easting_col = MagnetoPyFilesHelper.detect_column(raw_df.columns, 'longitude')
        if not easting_col:
            raise ValueError(f"Could not auto-detect easting/longitude column from headers: {list(raw_df.columns)}")
        log.info(f'Auto-detected easting column: {easting_col}')

    northing_col = getattr(arguments, 'northing_col', None)
    if not northing_col:
        northing_col = MagnetoPyFilesHelper.detect_column(raw_df.columns, 'latitude')
        if not northing_col:
            raise ValueError(f"Could not auto-detect northing/latitude column from headers: {list(raw_df.columns)}")
        log.info(f'Auto-detected northing column: {northing_col}')

    magnetic_field_col = getattr(arguments, 'magnetic_field_col', None)
    if not magnetic_field_col:
        magnetic_field_col = MagnetoPyFilesHelper.detect_column(raw_df.columns, 'magnetic_field')
        if not magnetic_field_col:
            raise ValueError(f"Could not auto-detect magnetic field column from headers: {list(raw_df.columns)}")
        log.info(f'Auto-detected magnetic field column: {magnetic_field_col}')

    required_cols = [easting_col, northing_col, magnetic_field_col] + ([upward_col] if upward_col else [])
    project_df = MagnetoPyFilesHelper.read_and_verify_columns(_project_file_path, required_cols)
    if project_df is None:
        log.error('Error reading the project file')
        return

    try:
        if _is_regular_grid(project_df, easting_col, northing_col):
            log.info('Regular grid detected; using the existing grid directly.')
            grid = _prepare_regular_grid(project_df, easting_col, northing_col, magnetic_field_col)
        elif use_equivalent_sources:
            log.info('Irregular grid detected; using equivalent-sources approximation.')
            grid = _equivalent_sources_grid(project_df, easting_col, northing_col, magnetic_field_col, upward_col)
        else:
            log.info('Irregular grid detected; using default Verde spline interpolation.')
            grid = _interpolate_to_regular_grid(project_df, easting_col, northing_col, magnetic_field_col, upward_col)
    except (ValueError, TypeError) as exc:
        log.error(f'Invalid grid for RTP transformation: {exc}')
        return

    log.info('Running Harmonica reduction-to-pole')
    reduced = harmonica.reduction_to_pole(
        grid=grid,
        inclination=inclination,
        declination=declination,
        magnetization_inclination=magnetization_inclination,
        magnetization_declination=magnetization_declination,
    )

    output_dir = os.path.join(os.path.abspath('resources'), _project_name)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = pd.Timestamp.now().strftime('%Y-%m-%d_%H%M%S')
    output_file = os.path.join(output_dir, f'{_project_name}_{timestamp}.csv')

    reduced_df = reduced.to_dataframe(name='reduction_to_pole').reset_index()
    reduced_df.to_csv(output_file, index=False)

    log.info(f'Reduction-to-pole results saved in: {output_file}')
    log.info('Reduction-to-pole completed successfully')
