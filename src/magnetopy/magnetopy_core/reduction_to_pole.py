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


class ReductionToPole:
    def __init__(self, arguments: Namespace):
        self.__magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='ReductionToPole')

        self.project_name: str = arguments.project_name
        self.project_file: str = arguments.project_file
        self.easting_col: str = arguments.easting_col
        self.northing_col: str = arguments.northing_col
        self.magnetic_field_col: str = arguments.magnetic_field_col
        self.upward_col: str | None = getattr(arguments, 'upward_col', None)
        self.equivalent_sources: bool = getattr(arguments, 'equivalent_sources', False)
        self.inclination: float = arguments.inclination
        self.declination: float = arguments.declination
        self.magnetization_inclination: float | None = getattr(arguments, 'magnetization_inclination', None)
        self.magnetization_declination: float | None = getattr(arguments, 'magnetization_declination', None)

        self.__reduction_to_pole()

    def __is_regular_grid(self, df: pd.DataFrame) -> bool:
        """
        Check whether the data already form a regular grid with constant spacing in both axes.
        """
        required_cols = [self.easting_col, self.northing_col]
        x_values = pd.to_numeric(df[self.easting_col], errors='coerce').dropna().drop_duplicates().sort_values().to_numpy()
        y_values = pd.to_numeric(df[self.northing_col], errors='coerce').dropna().drop_duplicates().sort_values().to_numpy()

        if len(x_values) < 2 or len(y_values) < 2:
            return False

        x_step = np.diff(x_values)
        y_step = np.diff(y_values)

        if np.any(x_step <= 0) or np.any(y_step <= 0):
            return False

        return np.allclose(x_step, x_step[0], rtol=1e-5, atol=1e-8) and np.allclose(y_step, y_step[0], rtol=1e-5, atol=1e-8)

    def __prepare_regular_grid(self, df: pd.DataFrame) -> xr.DataArray:
        """
        Convert the tabular CSV grid to an xarray DataArray used by Harmonica.
        """
        grid_df = df[[self.easting_col, self.northing_col, self.magnetic_field_col]].copy()
        grid_df[self.easting_col] = pd.to_numeric(grid_df[self.easting_col], errors='raise')
        grid_df[self.northing_col] = pd.to_numeric(grid_df[self.northing_col], errors='raise')
        grid_df[self.magnetic_field_col] = pd.to_numeric(grid_df[self.magnetic_field_col], errors='raise')

        x = pd.Index(grid_df[self.easting_col].drop_duplicates().sort_values(), name=self.easting_col)
        y = pd.Index(grid_df[self.northing_col].drop_duplicates().sort_values(), name=self.northing_col)

        data = grid_df.pivot(index=self.northing_col, columns=self.easting_col, values=self.magnetic_field_col)
        data = data.reindex(index=y, columns=x)

        data_array = xr.DataArray(
            data.to_numpy(),
            coords={'northing': y, 'easting': x},
            dims=('northing', 'easting'),
            name=self.magnetic_field_col,
        )

        return data_array

    def __interpolate_to_regular_grid(self, df: pd.DataFrame) -> xr.DataArray:
        """
        Interpolate irregular data onto a regular grid with Verde spline interpolation.
        The default behavior is a regularized spline, which is robust for most survey data.
        """
        points = {
            'easting': pd.to_numeric(df[self.easting_col], errors='raise'),
            'northing': pd.to_numeric(df[self.northing_col], errors='raise'),
            'data': pd.to_numeric(df[self.magnetic_field_col], errors='raise'),
        }

        if self.upward_col is not None:
            points['upward'] = pd.to_numeric(df[self.upward_col], errors='raise')

        if self.upward_col is not None:
            region = [points['easting'].min(), points['easting'].max(), points['northing'].min(), points['northing'].max()]
            grid_coords = verde.grid_coordinates(region=region, spacing=(np.median(np.diff(np.sort(np.unique(points['northing'])))), np.median(np.diff(np.sort(np.unique(points['easting']))))), extra_coords={'upward': np.mean(points['upward'])})
            spline = verde.Spline()
            interpolated = spline.fit((points['easting'], points['northing'], points['upward']), points['data'])
            grid = interpolated.grid(coordinates=grid_coords, data_names='magnetic_field')
        else:
            region = [points['easting'].min(), points['easting'].max(), points['northing'].min(), points['northing'].max()]
            spacing = (np.median(np.diff(np.sort(np.unique(points['northing'])))), np.median(np.diff(np.sort(np.unique(points['easting'])))))
            spline = verde.Spline()
            interpolated = spline.fit((points['easting'], points['northing']), points['data'])
            grid = interpolated.grid(region=region, spacing=spacing, data_names='magnetic_field')

        return grid['magnetic_field']

    def __equivalent_sources_grid(self, df: pd.DataFrame) -> xr.DataArray:
        """
        Approximate irregular data using Harmonica equivalent sources.
        This is especially useful when the data have significant height variation, as in aeromagnetic surveys.
        """
        easting = pd.to_numeric(df[self.easting_col], errors='raise').to_numpy()
        northing = pd.to_numeric(df[self.northing_col], errors='raise').to_numpy()
        magnetic = pd.to_numeric(df[self.magnetic_field_col], errors='raise').to_numpy()

        if self.upward_col is None:
            upward = np.zeros_like(easting, dtype=float)
        else:
            upward = pd.to_numeric(df[self.upward_col], errors='raise').to_numpy()

        region = [easting.min(), easting.max(), northing.min(), northing.max()]
        grid_coords = verde.grid_coordinates(region=region, spacing=(np.median(np.diff(np.sort(np.unique(northing)))), np.median(np.diff(np.sort(np.unique(easting))))), extra_coords={'upward': 0})

        equivalent_sources = harmonica.EquivalentSources(depth='default')
        fitted = equivalent_sources.fit((easting, northing, upward), magnetic)
        grid = fitted.grid(coordinates=(grid_coords[0], grid_coords[1], grid_coords[2]), data_names='magnetic_field')

        return grid['magnetic_field']

    def __reduction_to_pole(self) -> None:
        """
        Performs a reduction-to-pole transformation using Harmonica.
        If the input is irregular, it is first gridded using the default Verde spline interpolation,
        or approximated with equivalent sources when requested.

        :return: Nothing to return
        :rtype: None
        """
        self.__magnetopy_logging.info('Validating the project grid and preparing the RTP input')

        project_df = MagnetoPyFilesHelper.read_and_verify_columns(
            self.project_file,
            [self.easting_col, self.northing_col, self.magnetic_field_col] + ([self.upward_col] if self.upward_col else []),
        )

        if project_df is None:
            self.__magnetopy_logging.error('Error reading the project file')
            return

        try:
            if self.__is_regular_grid(project_df):
                self.__magnetopy_logging.info('Regular grid detected; using the existing grid directly.')
                grid = self.__prepare_regular_grid(project_df)
            elif self.equivalent_sources:
                self.__magnetopy_logging.info('Irregular grid detected; using equivalent-sources approximation.')
                grid = self.__equivalent_sources_grid(project_df)
            else:
                self.__magnetopy_logging.info('Irregular grid detected; using default Verde spline interpolation.')
                grid = self.__interpolate_to_regular_grid(project_df)
        except (ValueError, TypeError) as exc:
            self.__magnetopy_logging.error(f'Invalid grid for RTP transformation: {exc}')
            return

        if self.magnetization_inclination is None:
            magnetization_inclination = self.inclination
        else:
            magnetization_inclination = self.magnetization_inclination

        if self.magnetization_declination is None:
            magnetization_declination = self.declination
        else:
            magnetization_declination = self.magnetization_declination

        self.__magnetopy_logging.info('Running Harmonica reduction-to-pole')
        reduced = harmonica.reduction_to_pole(
            grid=grid,
            inclination=self.inclination,
            declination=self.declination,
            magnetization_inclination=magnetization_inclination,
            magnetization_declination=magnetization_declination,
        )

        output_dir = os.path.abspath(os.path.join(os.path.dirname(self.project_file), '..'))
        output_dir = os.path.join(output_dir, self.project_name)
        os.makedirs(output_dir, exist_ok=True)

        timestamp = pd.Timestamp.now().strftime('%Y-%m-%d_%H%M%S')
        output_file = os.path.join(output_dir, f'{self.project_name}_{timestamp}.csv')

        reduced_df = reduced.to_dataframe(name='reduction_to_pole').reset_index()
        reduced_df.to_csv(output_file, index=False)

        self.__magnetopy_logging.info(f'Reduction-to-pole results saved in: {output_file}')
        self.__magnetopy_logging.info('Reduction-to-pole completed successfully')

        return None
