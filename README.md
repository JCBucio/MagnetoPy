# Overview

MagnetoPy is an open-source Command Line Interface (CLI) written in Python, designed to process magnetic data. With a robust set of commands, MagnetoPy aims to simplify the analysis and manipulation of magnetic data for geophysicists in the field.

## Features

- **Diurnal variation correction**: MagnetoPy command that calculate the diurnal variation using field and base station data.

- **IGRF-14 correction**: MagnetoPy command that calculate the total magnetic field intensity from the IGRF-14 coefficients using field data and base stations.

- **Profile plotting**: MagnetoPy command that reads a project CSV and plots the temporal or spatial profile of a selected column.

- **Map plotting**: MagnetoPy command that displays geographic locations from a dataset as a map for quick spatial inspection (pure matplotlib, no system geospatial libraries required).

- **Reduction to the Pole (RTP)**: MagnetoPy command that compute the reduction to the pole of magnetic data using frequency domain calculations through Fast Fourier Transform.

## Installation

Check the `docs/ENVIRONMENT_MANUAL.md` file to prepare your environment using Conda.

## Usage

Check the `docs/HOW_TO_USE.md` file to learn how to use the CLI.

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

3. Run the CLI directly using positional file arguments and auto-detection:

```bash
# Diurnal variation
python magnetopy.py diurnal-variation resources/data_examples/cerritos_datos_estaciones.csv resources/data_examples/cerritos_estaciones_base.csv

# Calculate IGRF and total magnetic anomaly
python magnetopy.py calculate-igrf resources/data_examples/cerritos_datos_estaciones.csv --altitude 1.92

# Plot profile
python magnetopy.py plot-profile resources/cerritos_datos_estaciones/cerritos_datos_estaciones_*.csv

# Plot map
python magnetopy.py plot-map resources/data_examples/cerritos_datos_estaciones.csv
```

4. Inspect outputs in the `resources/` folder (CSV results, PNG plots).

## Contributing

Contributions to MagnetoPy are welcome! Whether you want to report a bug, request a feature, or submit a pull request, please refer to the [Contribution Guidelines](https://github.com/JCBucio/MagnetoPy/CONTRIBUTING.md).

## License

MagnetoPy is licensed under the MIT License. See [LICENSE](https://github.com/JCBucio/MagnetoPy/LICENSE) for more information.

## Contact

For questions, feedback, or support, feel free to contact me at [jcbucio.geo@gmail.com](mailto:jcbucio.geo@gmail.com).

## More information
If you want to know more about how *MagnetoPy* works and you would like to see more examples, you can visit this link on my website where I explain *MagnetoPy* in more depth: 
- [https://jcbucio.github.io/portafolio/MagnetoPy](https://jcbucio.github.io/portafolio/MagnetoPy)