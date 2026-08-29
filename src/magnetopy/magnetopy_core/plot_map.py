from argparse import Namespace
from logging import getLogger
import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
matplotlib.use('Agg')
from matplotlib import scale
import matplotlib.pyplot as plt
import pandas as pd

from src.magnetopy.magnetopy_utils.magnetopy_files_helper import MagnetoPyFilesHelper
from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging


class PlotMap:
    def __init__(self, arguments: Namespace):
        self.__magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='PlotMap')

        self.project_file: str = arguments.project_file
        self.latitude_col: str = arguments.latitude_col
        self.longitude_col: str = arguments.longitude_col

        self.__plot_map()

    def _calculate_dynamic_margins(self, lat_min: float, lat_max: float, lon_min: float, lon_max: float, padding_pct: float = 0.25) -> tuple[float, float]:
        """
        Calculates proportional map margins. Larger areas get larger padding, 
        while extremely small areas default to a high-zoom minimum.
        """
        lat_spread = lat_max - lat_min
        lon_spread = lon_max - lon_min
        
        # 0.00005 degrees is roughly 5.5 meters
        absolute_min_margin = 0.00005 

        # If spread is 0 (only one point exists), use the absolute minimum to prevent a blank map
        # Otherwise, pad by the given percentage, ensuring it never shrinks below the absolute minimum
        lat_margin = absolute_min_margin if lat_spread == 0 else max(absolute_min_margin, lat_spread * padding_pct)
        lon_margin = absolute_min_margin if lon_spread == 0 else max(absolute_min_margin, lon_spread * padding_pct)

        return lat_margin, lon_margin

    def __plot_map(self) -> None:
        """
        Reads the project file and plots the geographic location of the points.

        :return: Nothing to return
        :rtype: None
        """
        self.__magnetopy_logging.info('Reading the project file and plotting the geographic points')

        _project_file_path = self.project_file
        _latitude_col = self.latitude_col
        _longitude_col = self.longitude_col

        project_df = MagnetoPyFilesHelper.read_and_verify_columns(_project_file_path, [_latitude_col, _longitude_col])

        if project_df is None:
            self.__magnetopy_logging.error('Error reading the project file')
            return

        try:
            project_df[_latitude_col] = pd.to_numeric(project_df[_latitude_col], errors='raise')
            project_df[_longitude_col] = pd.to_numeric(project_df[_longitude_col], errors='raise')
        except ValueError as exc:
            self.__magnetopy_logging.error(f'Invalid numeric values in the latitude/longitude columns: {exc}')
            return

        for latitude in project_df[_latitude_col]:
            MagnetoPyFilesHelper.check_lat_bounds(float(latitude))

        for longitude in project_df[_longitude_col]:
            MagnetoPyFilesHelper.check_lon_bounds(float(longitude))

        output_dir = os.path.dirname(os.path.abspath(_project_file_path))
        output_file = os.path.join(output_dir, f'{os.path.splitext(os.path.basename(_project_file_path))[0]}_map.png')

        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())

        # FIX 1 & 2: Use '10m' for better regional detail and force zorder=0 so they sit at the back
        scale = '10m' 
        ax.add_feature(cfeature.LAND.with_scale(scale), facecolor='lightgray', edgecolor='gray', zorder=0)
        ax.add_feature(cfeature.OCEAN.with_scale(scale), facecolor='white', zorder=0)
        ax.add_feature(cfeature.COASTLINE.with_scale(scale), linewidth=0.5, zorder=1)
        ax.add_feature(cfeature.BORDERS.with_scale(scale), linestyle='--', edgecolor='gray', zorder=1)

        # Add state/province boundaries to give inland maps context
        ax.add_feature(cfeature.STATES.with_scale(scale), edgecolor='gray', linewidth=0.5, zorder=1)

        # Add lakes and rivers with a light blue color to enhance geographic context
        ax.add_feature(cfeature.LAKES.with_scale(scale), facecolor='lightblue', zorder=1)
        ax.add_feature(cfeature.RIVERS.with_scale(scale), edgecolor='lightblue', zorder=1)

        # Optional: If you want a textured satellite/topographic base map instead of flat colors, uncomment below:
        ax.stock_img()

        lat_min = float(project_df[_latitude_col].min())
        lat_max = float(project_df[_latitude_col].max())
        lon_min = float(project_df[_longitude_col].min())
        lon_max = float(project_df[_longitude_col].max())

        lat_margin, lon_margin = self._calculate_dynamic_margins(lat_min, lat_max, lon_min, lon_max)

        # FIX 4: Clamp the extents so they don't exceed physical geographic boundaries
        ext_lon_min = max(-180.0, lon_min - lon_margin)
        ext_lon_max = min(180.0, lon_max + lon_margin)
        ext_lat_min = max(-90.0, lat_min - lat_margin)
        ext_lat_max = min(90.0, lat_max + lat_margin)

        ax.set_extent([ext_lon_min, ext_lon_max, ext_lat_min, ext_lat_max], crs=ccrs.PlateCarree())

        # FIX 2: Explicitly set a high zorder for the scatter plot so points are never hidden
        ax.scatter(project_df[_longitude_col], project_df[_latitude_col], 
                   s=50, c='tab:blue', edgecolors='black', 
                   transform=ccrs.PlateCarree(), zorder=5)

        # FIX 3: Use gridlines for lat/lon formatting instead of standard set_xlabel/set_ylabel
        gl = ax.gridlines(draw_labels=True, crs=ccrs.PlateCarree(), color='gray', alpha=0.5, linestyle='--', zorder=2)
        gl.top_labels = False   # Hide labels on the top axis
        gl.right_labels = False # Hide labels on the right axis
        
        ax.set_title('Magnetic data points by location')

        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close(fig)

        self.__magnetopy_logging.info(f'Map saved in {output_file}')
        self.__magnetopy_logging.info('Map plotted successfully')
