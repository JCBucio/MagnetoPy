# Overview
*MagnetoPy* is a Python script that calculates diurnal variation and requests total magnetic field intensity from an IGRF API using field data and base stations.

## Installation
Download the [zip file](https://github.com/JCBucio/MagnetoPy/archive/refs/heads/main.zip) or use `git clone` to clone the repository to a working directory (e.g., `/Users/jcbucio/MagnetoPy/`). All scripts will be run from this directory, and all new files will be generated here.

From the files that will get downloaded, you only need the `magnetopy.exe` file. You can put this file wherever you want in your filesystem, you can add it to your desktop for convenience purposes. The rest of the files are the source code of the program.

## Usage for Windows
To check if *MagnetoPy* was installed correctly, simply double click the `magnetopy.exe` file or run the following command from the working directory where the program is located:
```
magnetopy.exe
```
If the dependencies were installed correctly you should see a command line opened with the following output:
```
############## MAGNETIC FIELD DATA FORMATTER ##############
##                                                       ##  
##  Written by Juan Carlos Bucio (jcbucio.geo@gmail.com) ##
##               Licensed under MIT license              ##
##                                                       ##
###########################################################

--- FILES NAMES PARAMETERS ---

Stations file name and path:
```
If you don't see a command line opened, please inform about the problem to the author.

### Processing magnetic data
To begin with the processing of magnetic data, we must pass to *MagnetoPy* the following parameters:

- **`stationsfile`**: Path to the file containing the magnetic data files from field stations.
- **`basefile`**: Path to the file containing the magnetic data files from base stations.
- **`outputfile`**: Path to the file where the output will be saved.

**NOTE:** It is important to check that your files have `UTF-8` enconding.

The `stationsfile` must contain the following columns:
- **date**: Date of the measurement in DD/MM/YYYY format.
- **time**: Time of the measurement in HH:MM:SS format.
- **magfield**: Magnetic field intensity in nT from each station.
- **lat**: Latitude of the station in decimal degrees.
- **lon**: Longitude of the station in decimal degrees.

The `basefile` must contain the following columns:
- **date**: Date of the measurement in DD/MM/YYYY format.
- **time**: Time of the measurement in HH:MM:SS format.
- **magfield**: Magnetic field intensity in nT from each base station measurement.

Aditionally to the previous information, the `outputfile` will display the following data:
- **diff_time**: Time difference between the station measurement and the base station measurement.
- **base_magfield_mean**: Mean magnetic field intensity from the base stations for one day.
- **diurnal_var**: Diurnal variation of the magnetic field intensity.
- **diurnal_var_corr**: Correction of diurnal variation.
- **igrf_intensity**: Total magnetic field intensity from the IGRF model.
- **igrf_res_field**: Residual magnetic field calculated with the total magnetic field intensity from the IGRF model.

## Convert GPX files to CSV
In addition, the repository has a program `gpx_converter.py` that helps us convert gpx files to csv in the event that our mobile stations have been processed in some software such as Google Earth or any GIS (Geographic Information System). To make use of the program you first need to install `gpxpy` once your conda environment is activated:

```
>> conda install -c conda-forge gpxpy
```

Now you can convert your gpx files to a csv with the following command:

```
>> python gpx_converter.py gpx_file csv_output_file
```

## More information
If you want to know more about how *MagnetoPy* works and you would like to see more examples, you can visit this link on my website where I explain *MagnetoPy* in more depth: 
- [https://jcbucio.github.io/portafolio/MagnetoPy](https://jcbucio.github.io/portafolio/MagnetoPy)