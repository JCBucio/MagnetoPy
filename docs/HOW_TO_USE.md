# How to use MagnetoPy

---
## Environment manual
You can review the [ENVIRONMENT_MANUAL.md][environment_manual] file in the MagnetoPy documentation to prepare your environment.

---
## Get help
MagnetoPy help:

    --help

```sh
python magnetopy.py --help
```

Help by command:

    diurnal-variation --help

```sh
python magnetopy.py <command> --help
```

---
## Available commands in magnetopy-cli
    Commands: diurnal-variation, calculate-igrf, reduction-to-pole (in development), plot-profile.

___
### diurnal-variation
    Command: diurnal-variation [options]

    MagnetoPy command that calculate the diurnal variation using field data and base station registers.

    --project_name <value>          Project name (required).
    --stations_file <value>         Stations file path containing date, time, magfield, latitude and longitude data of the study (required).
    --stations_cols <value>         Stations file columns names in the following order: date, time, latitude, longitude and magnetic_field (required).
    --base_station_file <value>     Base station file path containing date, time and magfield of the study (required).
    --base_stations_cols <value>    Base station columns names in the following order: date, time and magnetic_field (required).

        Example:

```sh
python magnetopy.py diurnal-variation \
    --project_name cerritos_test \
    --stations_file resources/data_examples/cerritos_datos_estaciones.csv \
    --stations_cols date,time,latitude,longitude,magfield \
    --base_station_file resources/data_examples/cerritos_estaciones_base.csv \
    --base_station_cols date,time,magfield
```

___
### calculate-igrf
    Command: calculate-igrf [options]

    MagnetoPy command that calculate the total magnetic field intensity from the IGRF-14 coefficients using field data and base stations.

    --project_name <value>          Project name (required).
    --stations_file <value>         Stations file path containing date, time, magfield, latitude and longitude data of the study (required).
    --stations_cols <value>         Stations file columns names in the following order: date, time, magfield, latitude and longitude (required).
    --altitude <value>              Altitude of the study area in kilometers (required).
    --date <value>                  Date of the study in the format YYYY-MM-DD (required).
    
        Example:

```sh
python magnetopy.py calculate-igrf \
    --project_name cerritos_test \
    --stations_file resources/data_examples/cerritos_datos_estaciones.csv \
    --stations_cols date,time,magfield,latitude,longitude \
    --altitude 1.920 \
    --date 2019-03-26
```
___
### reduction-to-pole (in development)
    Command: reduction-to-pole [options]

    MagnetoPy command that compute the reduction to the pole of magnetic data using frequency domain calculations through Fast Fourier Transform.

___
### plot-profile
    Command: plot-profile [options]

    MagnetoPy command that plot the profile of a selected column in the data.

    --project_file <value>          Project file to be read (required).
    --col_to_plot <value>           Column to plot (required).

        Example:

```sh
python magnetopy.py plot-profile \
    --project_file resources/cerritos_test/cerritos_test_2026-05-08_223841.csv \
    --col_to_plot diurnal_var_corr
```

___

### plot-map
        Command: plot-map [options]

        MagnetoPy command that plots geographic locations of magnetic data points contained in a CSV file. Useful to quickly visualise station distributions.

        --project_file <value>          Project CSV file path to be read (required).
        --latitude_col <value>          Column name containing latitude values in the CSV (required).
        --longitude_col <value>         Column name containing longitude values in the CSV (required).

        Example:

```sh
python magnetopy.py plot-map \
    --project_file resources/data_examples/cerritos_datos_estaciones.csv \
    --latitude_col gpslat \
    --longitude_col gpslon
```

        The command saves a PNG map next to the input CSV (e.g. `cerritos_datos_estaciones_map.png`).
### Further information
If there are still some doubts about the usage of these commands, you can check this post on my blog with a example of how to use the CLI:
[MagnetoPy](https://jcbucio.github.io/portafolio/MagnetoPy)