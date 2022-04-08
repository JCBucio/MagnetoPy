## Overview
MagnetoPy is a Python script that calculates diurnal variation and requests total magnetic field intensity from an IGRF API using field data and base stations.

## Installation
Download the [zip file](https://github.com/JCBucio/MagnetoPy/archive/refs/heads/main.zip) or use `git` to clone the repository to a working directory (e.g., `/Users/jcbucio/MagnetoPy/`). All scripts will be run from this directory, and all new files will be generated here.

MagnetoPy runs on Python 3.8+, with the following dependencies:
[numpy](https://numpy.org/) | [pandas](https://pandas.pydata.org/)

This dependencies can be easily installed via [Anaconda](https://www.anaconda.com/) on the command line. I *highly* recommend using a virtual environment so that your MagnetoPy environment does not conflict with other Python packages.
This can be done with the following commands:
```
>> conda create -n magnetopy python=3.8 numpy pandas
```

## Usage
To check if MagnetoPy was installed correctly, simply run the following command:
```
>> python magnetopy.py
```

