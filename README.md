# Overview

MagnetoPy is an open-source Command Line Interface (CLI) written in Python, designed to process magnetic data. With a robust set of commands, MagnetoPy aims to simplify the analysis and manipulation of magnetic data for geophysicists in the field.

## Features

- **Diurnal variation correction**: MagnetoPy command that calculate the diurnal variation using field and base station data.

- **IGRF-14 correction**: MagnetoPy command that calculate the total magnetic field intensity from the IGRF-14 coefficients using field data and base stations.

- **Reduction to the Pole (RTP)**: MagnetoPy command that compute the reduction to the pole of magnetic data using frequency domain calculations through Fast Fourier Transform.

## Installation

Check the ENVIROMENT_MANUAL.md file in the `docs` folder to prepare your environment.

## Usage

Check the HOW_TO_USE.md file in the `docs` folder to learn how to use the CLI.

## Quick start

1. Create and activate a Python virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install project dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Run example commands (adjust paths/column names as needed):

```bash
# Diurnal variation
python magnetopy.py diurnal-variation \
	--project_name cerritos_test \
	--stations_file resources/data_examples/cerritos_datos_estaciones.csv \
	--stations_cols date,time,latitude,longitude,magfield \
	--base_station_file resources/data_examples/cerritos_estaciones_base.csv \
	--base_station_cols date,time,magfield

# Calculate IGRF
python magnetopy.py calculate-igrf \
	--project_name cerritos_test \
	--stations_file resources/data_examples/cerritos_datos_estaciones.csv \
	--stations_cols date,time,magfield,latitude,longitude \
	--altitude 1.920 \
	--date 2019-03-26

# Plot profile
python magnetopy.py plot-profile \
	--project_file resources/cerritos_test/cerritos_test_2026-05-08_223841.csv \
	--col_to_plot diurnal_var_corr

# Plot map
python magnetopy.py plot-map \
	--project_file resources/data_examples/cerritos_datos_estaciones.csv \
	--latitude_col gpslat \
	--longitude_col gpslon
```

4. Inspect outputs in the `resources/` folder (CSV results, PNG plots).

## Troubleshooting

Cartopy (used by the `plot-map` command) depends on system geospatial libraries which may not be present on all systems. If `pip install -r requirements.txt` fails for `cartopy`, try one of the following:

- On Debian/Ubuntu, install system packages first:

```bash
sudo apt update && sudo apt install -y libproj-dev proj-data proj-bin libgeos-dev
python -m pip install -r requirements.txt
```

- If you use Conda, prefer installing Cartopy and its binary dependencies from conda-forge:

```bash
conda create -n magnetopy python=3.11 -y
conda activate magnetopy
conda install -c conda-forge cartopy matplotlib pandas scipy numpy -y
python -m pip install -r requirements.txt --no-deps
```

- If problems persist, consult the Cartopy installation notes: https://scitools.org.uk/cartopy/docs/latest/installing.html

## Contributing

Contributions to MagnetoPy are welcome! Whether you want to report a bug, request a feature, or submit a pull request, please refer to the [Contribution Guidelines](https://github.com/JCBucio/MagnetoPy/CONTRIBUTING.md).

## License

MagnetoPy is licensed under the MIT License. See [LICENSE](https://github.com/JCBucio/MagnetoPy/LICENSE) for more information.

## Contact

For questions, feedback, or support, feel free to contact me at [jcbucio.geo@gmail.com](mailto:jcbucio.geo@gmail.com).

## More information
If you want to know more about how *MagnetoPy* works and you would like to see more examples, you can visit this link on my website where I explain *MagnetoPy* in more depth: 
- [https://jcbucio.github.io/portafolio/MagnetoPy](https://jcbucio.github.io/portafolio/MagnetoPy)