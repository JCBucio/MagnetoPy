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

This will install the required libraries for MagnetoPy, including pandas, numpy, scipy, matplotlib, and the optional geophysical tools used by the reduction-to-pole workflow.

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
python magnetopy.py calculate-igrf --config resources/config_templates/calculate_igrf_config.yaml
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