# Overview

MagnetoPy is an open-source Command Line Interface (CLI) written in Python, designed to process magnetic data. With a robust set of commands, MagnetoPy aims to simplify the analysis and manipulation of magnetic data for geophysicists in the field.

## Features

- **Diurnal variation correction**: MagnetoPy command that calculate the diurnal variation using field and base station data.

- **IGRF correction**: MagnetoPy command that calculate the total magnetic field intensity from the IGRF coefficients using field data and base stations.

- **Reduction to the Pole (RTP)**: MagnetoPy command that compute the reduction to the pole of magnetic data using frequency domain calculations through Fast Fourier Transform.

## Installation

Before installing MagnetoPy, ensure you have Python 3.11 or higher installed on your system.

1. Download the [zip file](https://github.com/JCBucio/MagnetoPy/archive/refs/heads/main.zip) of the project or `git clone` the repository to a working directory (e.g., `/Users/jcbucio/tools/`). All commands will be run from this directory, and all new files will be generated here.
2. Open a command prompt or terminal and navigate to the project folder.
3. Create a virtual environment with the desired name:

```bash
python -m venv magnetopy_env
```

4. Activate the virtual environment:

For Windows:
```bash
magnetopy_env\Scripts\activate
```

For Linux:
```bash
source magnetopy_env/bin/activate
```

5. Install the project dependencies using the requirements.txt file:

```bash
python -m pip install -r requirements.txt
```

6. Verify the installation by running the following command:

```bash
python magnetopy.py
```

If successful, you should see the usage information for MagnetoPy. If not, please review the installation steps or contact me to [jcbucio.geo@gmail.com](mailto:jcbucio.geo@gmail.com) for assistance.

## Usage

To start using MagnetoPy, simply run the CLI and explore the available commands:

```bash
python magnetopy.py
```

For detailed usage instructions and command documentation, refer to the [Documentation](https://github.com/JCBucio/MagnetoPy/docs).

## Contributing

Contributions to MagnetoPy are welcome! Whether you want to report a bug, request a feature, or submit a pull request, please refer to the [Contribution Guidelines](https://github.com/JCBucio/MagnetoPy/CONTRIBUTING.md).

## License

MagnetoPy is licensed under the MIT License. See [LICENSE](https://github.com/JCBucio/MagnetoPy/LICENSE) for more information.

## Contact

For questions, feedback, or support, feel free to contact me at [jcbucio.geo@gmail.com](mailto:jcbucio.geo@gmail.com).

## More information
If you want to know more about how *MagnetoPy* works and you would like to see more examples, you can visit this link on my website where I explain *MagnetoPy* in more depth: 
- [https://jcbucio.github.io/portafolio/MagnetoPy](https://jcbucio.github.io/portafolio/MagnetoPy)