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

Output columns

The command creates a CSV file that keeps the original station records and adds the diurnal correction values. The columns are usually written with the prefixes `sta_` and `base_` to distinguish the survey data from the base-station data.

- `sta_date` / `sta_time`: date and time of each field observation.
- `sta_latitude` / `sta_longitude`: geographic coordinates of the station.
- `sta_magnetic_field`: measured magnetic field value at the station.
- `sta_datetime`: combined datetime value used for time matching.
- `base_date` / `base_time`: date and time of the corresponding base-station measurement.
- `base_magnetic_field`: raw magnetic field value recorded by the base station.
- `base_datetime`: datetime of the base-station measurement.
- `base_magfield_mean`: mean magnetic field of the base station for that date (used as the daily reference level).
- `time_diff`: absolute time difference between the station record and the matched base-station record.
- `diurnal_var`: base-station variation relative to the daily mean, computed as `base_magnetic_field - base_magfield_mean`.
- `diurnal_var_corr`: corrected magnetic value after removing the diurnal component, computed as `sta_magnetic_field - diurnal_var`.

This means the final corrected field is the station field corrected by the estimated diurnal variation measured at the base station.

___
### calculate-igrf
    Command: calculate-igrf [options]

    MagnetoPy command that calculate the total magnetic field intensity from the IGRF-14 coefficients using field data and base stations.

    --project_name <value>          Project name (required).
    --stations_file <value>         Stations file path containing date, time, magfield, latitude and longitude data of the study (required).
    --stations_cols <value>         Stations file columns names in the following order: date, time, magfield, latitude and longitude (required).
    --altitude <value>              Altitude of the study area in kilometers (required).
    --date <value>                  Date of the study in the format YYYY-MM-DD (required).
    --verbose                       Include the IGRF secular-variation columns in the output CSV.

        Example:

```sh
python magnetopy.py calculate-igrf \
    --project_name cerritos_test \
    --stations_file resources/data_examples/cerritos_datos_estaciones.csv \
    --stations_cols date,time,magfield,latitude,longitude \
    --altitude 1.920 \
    --date 2019-03-26
```

Output columns

By default, the command writes the main magnetic field components and the station metadata. The exact names depend on the column names supplied in `--stations_cols`, but the output always includes the following standard IGRF fields:

- `date`: date of the observation.
- `time`: time of the observation.
- `latitude` / `longitude`: station coordinates used to compute the model.
- `magfield`: original measured magnetic field value.
- `datetime`: combined date-time value used internally.
- `decimal_date`: date expressed as a decimal year, used for the IGRF interpolation.
- `igrf_date`: the same decimal-date reference used for the IGRF calculation.
- `D(°)`: magnetic declination, in degrees.
- `I(°)`: magnetic inclination, in degrees.
- `H(nT)`: horizontal magnetic intensity, in nT.
- `F(nT)`: total magnetic intensity, in nT.
- `X(nT)`: north component of the magnetic field, in nT.
- `Y(nT)`: east component of the magnetic field, in nT.
- `Z(nT)`: vertical component of the magnetic field, in nT.

When the `--verbose` option is enabled, the following secular-variation columns are also added:

- `SV_D(min/yr)`: rate of change of declination, in arcminutes per year.
- `SV_I(min/yr)`: rate of change of inclination, in arcminutes per year.
- `SV_H(nT/yr)`: rate of change of the horizontal field component, in nT/year.
- `SV_F(nT/yr)`: rate of change of the total field intensity, in nT/year.
- `SV_X(nT/yr)`: rate of change of the north component, in nT/year.
- `SV_Y(nT/yr)`: rate of change of the east component, in nT/year.
- `SV_Z(nT/yr)`: rate of change of the vertical component, in nT/year.

These `SV_*` columns describe the secular variation of the IGRF field model, i.e., how each component changes with time at the selected date and location. They are useful for temporal interpretation and for understanding long-term field change, but the main core output remains the instantaneous field components (`D`, `I`, `H`, `F`, `X`, `Y`, `Z`).

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