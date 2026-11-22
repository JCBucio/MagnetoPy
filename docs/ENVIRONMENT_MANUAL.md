# Environment Manual

---
## Prepare the work environment

### Install Python
You can download Python from the official website [Python](https://www.python.org/downloads/).

> **Note**: MagnetoPy supports Python 3.11.0 or higher.

---

### Install Git
You can download Git from the official website [Git](https://git-scm.com/downloads).

---

### Install Conda
If you do not have Conda installed, install Miniconda or Anaconda from the official website:

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- [Anaconda](https://www.anaconda.com/products/distribution)

---

### Clone the repository
You can clone the repository using the following command:

```sh
git clone https://github.com/JCBucio/MagnetoPy.git
```

> **Note**: You can also download the repository as a zip file from the GitHub page, but cloning the repository is recommended because you can easily update it with the latest changes using `git pull`.

---

### Create a Conda environment
Open a terminal and run the following commands from the project root:

```sh
cd MagnetoPy
conda create -n magnetopy_env python=3.11 -y
conda activate magnetopy_env
```

> **Note**: You can use any environment name you prefer. In this example it is `magnetopy_env`.

---

### Install the project dependencies
From the project root, run:

```sh
pip install -r requirements.txt
```

This will install the required libraries for MagnetoPy, including pandas, numpy, scipy, matplotlib, and the optional geophysical tools used by the reduction-to-pole workflow. No system geospatial libraries (e.g., GEOS, PROJ) are required.

---

### Activate the environment when working on the project
Whenever you want to run MagnetoPy, open a terminal and execute:

```sh
conda activate magnetopy_env
cd MagnetoPy
```

Then run the CLI with the desired command. For example:

```sh
python magnetopy.py --help
python magnetopy.py calculate-igrf resources/data_examples/cerritos_datos_estaciones.csv --altitude 1.92
```

---

### Update the repository
To update the repository with the latest changes, use:

```sh
git pull origin main
```

Then reinstall dependencies if the `requirements.txt` file changed:

```sh
pip install -r requirements.txt
```

---

### More resources
If the process of setting up the environment is not clear, you can check the following resources:
- [MagnetoPy post](https://jcbucio.github.io/portafolio/MagnetoPy)

If you have any questions or need help, you can contact me at [jcbucio.geo@gmail.com](mailto:jcbucio.geo@gmail.com).

---

## Keeping your environment clean

A healthy Conda environment prevents mysterious dependency conflicts and keeps MagnetoPy reproducible across machines. Apply these habits regularly.

### Inspect what is installed

```sh
# List all pip-installed packages and their versions
pip list

# List all conda-managed packages (shows build strings and channels)
conda list

# Detect broken or incompatible dependency chains
pip check
```

### Update dependencies

After pulling a new version of MagnetoPy, reinstall requirements to pick up any changes:

```sh
pip install -r requirements.txt --upgrade
```

> **Note**: Only upgrade inside the active `magnetopy_env` environment to avoid modifying your base Conda installation.

### Remove and recreate the environment from scratch

If the environment becomes inconsistent or you want a clean slate:

```sh
conda deactivate
conda env remove -n magnetopy_env

conda create -n magnetopy_env python=3.11 -y
conda activate magnetopy_env
pip install -r requirements.txt
```

### Export the environment for reproducibility

Freeze the full environment so others (or a future you) can recreate it exactly:

```sh
# Export a cross-platform requirements file (pip-only)
pip freeze > requirements_lock.txt

# Export a full Conda environment spec (platform-specific, includes build hashes)
conda env export > environment.yml
```

> **Tip**: Commit `requirements_lock.txt` to the repository when you need bit-for-bit reproducibility. Use `requirements.txt` with version ranges for general usage.

### Avoid mixing conda and pip packages

Installing the same package through both `conda install` and `pip install` inside the same environment can cause silent conflicts. Follow this rule:

1. Create the environment with `conda create` and activate it.
2. Install **all** project dependencies through `pip install -r requirements.txt`.
3. Avoid running `conda install <package>` inside `magnetopy_env` unless the package is unavailable on PyPI.

### Keep the environment inactive when not in use

Always deactivate the environment after finishing your session:

```sh
conda deactivate
```

This prevents the MagnetoPy environment from interfering with other Python projects on your machine.