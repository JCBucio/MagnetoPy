# Overview

MagnetoPy is an open-source Command Line Interface (CLI) written in Python, designed to process magnetic data. With a robust set of commands, MagnetoPy aims to simplify the analysis and manipulation of magnetic data for geophysicists in the field.

## Features

- **Diurnal variation correction**: MagnetoPy command that calculate the diurnal variation using field and base station data.

- **IGRF-14 correction**: MagnetoPy command that calculate the total magnetic field intensity from the IGRF-14 coefficients using field data and base stations.

- **Profile plotting**: MagnetoPy command that reads a project CSV and plots the temporal or spatial profile of a selected column.

- **Map plotting**: MagnetoPy command that displays geographic locations from a dataset as a map for quick spatial inspection.

- **Reduction to the Pole (RTP)**: MagnetoPy command that compute the reduction to the pole of magnetic data using frequency domain calculations through Fast Fourier Transform.

## Installation

Check the `docs/ENVIRONMENT_MANUAL.md` file to prepare your environment using Conda.

## Usage

Check the `docs/HOW_TO_USE.md` file to learn how to use the CLI and the config-file workflow.

## Quick start

1. Create and activate a Conda environment:

```bash
conda create -n magnetopy_env python=3.11 -y
conda activate magnetopy_env
```

2. Install project dependencies:

```bash
pip install -r requirements.txt
```

3. Run the tool using config files (preferred workflow):

```bash
# Diurnal variation
python magnetopy.py diurnal-variation --config resources/config_templates/diurnal_variation_config.yaml

# Calculate IGRF
python magnetopy.py calculate-igrf --config resources/config_templates/calculate_igrf_config.yaml

# Plot profile
python magnetopy.py plot-profile --config resources/config_templates/plot_profile_config.yaml

# Plot map
python magnetopy.py plot-map --config resources/config_templates/plot_map_config.yaml

# Reduction to pole
python magnetopy.py reduction-to-pole --config resources/config_templates/reduction_to_pole_config.yaml
```

4. You can still override a value from the config file for a single run:

```bash
python magnetopy.py calculate-igrf --config resources/config_templates/calculate_igrf_config.yaml --date 2020-01-15
```

5. Inspect outputs in the `resources/` folder (CSV results, PNG plots).

## Troubleshooting

Cartopy (used by the `plot-map` command) depends on system geospatial libraries which may not be present on all systems. If `pip install -r requirements.txt` fails for `cartopy`, try one of the following:

- On Debian/Ubuntu, install system packages first:

```bash
sudo apt update && sudo apt install -y libproj-dev proj-data proj-bin libgeos-dev
python -m pip install -r requirements.txt
```

- If you use Conda, prefer installing Cartopy and its binary dependencies from conda-forge:

```bash
conda create -n magnetopy_env python=3.11 -y
conda activate magnetopy_env
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