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
    Commands: diurnal-variation, calculate-igrf, reduction-to-pole, plot-profile, plot-map.

___
### diurnal-variation
    Command: diurnal-variation <stations_file> <base_station_file> [options]

    MagnetoPy command that calculates the diurnal variation using field survey data and base station records.
    Columns (date, time, coordinates, magnetic field) and project name are auto-detected by default.

    Positional arguments:
    STATIONS_FILE                   Survey stations CSV file path.
    BASE_STATION_FILE               Base station CSV file path.

    Optional flags (overrides):
    --project_name <value>          Project name (defaults to stations file name).
    --stations_file <value>         Stations file path (if not passed positionally).
    --stations_cols <value>         Stations columns in order: date, time, latitude, longitude, magnetic_field.
    --base_station_file <value>     Base station file path (if not passed positionally).
    --base_station_cols <value>     Base station columns in order: date, time, magnetic_field.

        Fast Field Example (auto-detects columns):

```sh
python magnetopy.py diurnal-variation \
    resources/data_examples/cerritos_datos_estaciones.csv \
    resources/data_examples/cerritos_estaciones_base.csv
```

        Explicit Flags Example:

```sh
python magnetopy.py diurnal-variation \
    --project_name cerritos_test \
    --stations_file resources/data_examples/cerritos_datos_estaciones.csv \
    --stations_cols date,time,gpslat,gpslon,magfield \
    --base_station_file resources/data_examples/cerritos_estaciones_base.csv \
    --base_station_cols date,time,nT
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
    Command: calculate-igrf <stations_file> --altitude <km> [options]

    MagnetoPy command that calculates the geomagnetic reference field (IGRF-14) and computes
    the total magnetic anomaly (residual) for the survey dataset.
    Columns, survey date, and project name are auto-detected by default.

    Positional arguments:
    STATIONS_FILE                   Survey stations CSV file path.

    Required flags:
    --altitude <value>              Altitude of the study area in kilometers (required).

    Optional flags (overrides):
    --date <value>                  Date of the study in format YYYY-MM-DD (auto-detected from survey data if omitted).
    --project_name <value>          Project name (defaults to stations file name).
    --stations_file <value>         Stations file path (if not passed positionally).
    --stations_cols <value>         Stations columns in order: date, time, latitude, longitude, magnetic_field.
    --verbose                       Include IGRF secular-variation columns in output CSV.

        Fast Field Example (auto-detects date & columns):

```sh
python magnetopy.py calculate-igrf \
    resources/data_examples/cerritos_datos_estaciones.csv \
    --altitude 1.920
```

        Explicit Flags Example:

```sh
python magnetopy.py calculate-igrf \
    --project_name cerritos_test \
    --stations_file resources/data_examples/cerritos_datos_estaciones.csv \
    --stations_cols date,time,gpslat,gpslon,magfield \
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
- `mag_anomaly(nT)`: total magnetic anomaly (residual), calculated as the observed magnetic field minus the IGRF total intensity (`F(nT)`).

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
    Command: plot-profile <file> [column] [options]

    MagnetoPy command that plots the profile of a selected column in the data.
    Automatically detects the magnetic field / anomaly column if omitted.

    Positional arguments:
    FILE                            Project CSV file to be read.
    COLUMN                          Column to plot (optional, auto-detects magnetic/anomaly column if omitted).

    Optional flags:
    --project_file <value>          Project file path (if not passed positionally).
    --col_to_plot <value>           Column to plot (if not passed positionally).

        Fast Field Example:

```sh
python magnetopy.py plot-profile resources/cerritos_test/cerritos_test_2026-05-08_223841.csv
```

        With Explicit Column:

```sh
python magnetopy.py plot-profile \
    resources/cerritos_test/cerritos_test_2026-05-08_223841.csv \
    diurnal_var_corr
```

___

### plot-map
    Command: plot-map <file> [options]

    MagnetoPy command that plots geographic locations of magnetic data points contained in a CSV file.
    Coordinates (latitude and longitude) are auto-detected by default.

    Positional arguments:
    FILE                            Project CSV file path.

    Optional flags:
    --project_file <value>          Project CSV file path (if not passed positionally).
    --latitude_col <value>          Column name containing latitude values (auto-detected if omitted).
    --longitude_col <value>         Column name containing longitude values (auto-detected if omitted).

        Fast Field Example (auto-detects coordinates):

```sh
python magnetopy.py plot-map resources/data_examples/cerritos_datos_estaciones.csv
```

        The command saves a PNG map next to the input CSV (e.g. `cerritos_datos_estaciones_map.png`).

___

### reduction-to-pole
    Command: reduction-to-pole <file> --inclination <deg> --declination <deg> [options]

    MagnetoPy command that computes a reduction-to-pole magnetic grid using Harmonica.
    Coordinates, magnetic field column, and project name are auto-detected by default.

    Positional arguments:
    FILE                               Input CSV file with geophysical grid data.

    Required flags:
    --inclination <value>              Inclination of the inducing geomagnetic field in degrees (required).
    --declination <value>              Declination of the inducing geomagnetic field in degrees (required).

    Optional flags:
    --project_name <value>             Project name to store output CSV (defaults to file name).
    --project_file <value>             Input CSV file (if not passed positionally).
    --easting_col <value>              Column name for easting coordinates (auto-detected if omitted).
    --northing_col <value>             Column name for northing coordinates (auto-detected if omitted).
    --magnetic_field_col <value>       Column name for magnetic field values (auto-detected if omitted).
    --magnetization_inclination <val>  Optional magnetization inclination in degrees. Defaults to inducing field inclination.
    --magnetization_declination <val>  Optional magnetization declination in degrees. Defaults to inducing field declination.
    --upward_col <value>               Optional column containing altitude/upward coordinate values.
    --equivalent-sources               Use Harmonica EquivalentSources instead of default Verde spline interpolation.

        Fast Field Example (auto-detects grid columns):

```sh
python magnetopy.py reduction-to-pole \
    resources/data_examples/irregular_grid.csv \
    --inclination 45 \
    --declination 0
```

        Example with equivalent-sources approximation:

```sh
python magnetopy.py reduction-to-pole \
    --project_name rtp_aeromag \
    --project_file resources/data_examples/aeromag_grid.csv \
    --easting_col easting \
    --northing_col northing \
    --magnetic_field_col magnetic_field \
    --upward_col altitude \
    --inclination 55 \
    --declination 10 \
    --equivalent-sources
```

Output

The command saves a CSV file inside `resources/<project_name>/`. The output includes the reduced-to-pole magnetic field values in a regular grid format with the columns produced by Harmonica.

Notes

- The default path is `Verde.Spline` interpolation, used when the input grid is irregular.
- The `--equivalent-sources` option is useful for datasets with strong altitude variation, such as aeromagnetic data.
- If the input file is already on a regular grid, the command uses it directly without interpolation.

___
### Further information
If there are still some doubts about the usage of these commands, you can check this post on my blog with a example of how to use the CLI:
[MagnetoPy](https://jcbucio.github.io/portafolio/MagnetoPy)

---
## Using YAML config files

MagnetoPy supports parameter files so you can avoid typing long arguments on the command line. Define your preferred project setup in a JSON, YAML, or INI file and use it with `--config`.

Priority order is:

1. config file values
2. CLI arguments

Use the config file for the main project configuration and use CLI arguments only when you want to override a specific value for a single run.

This is especially useful for long file paths, repeated parameter sets, and project reproducibility.

### Example config files

The repository includes ready-to-use templates in `resources/config_templates/`:

- `diurnal_variation_config.yaml`
- `calculate_igrf_config.yaml`
- `plot_profile_config.yaml`
- `plot_map_config.yaml`
- `reduction_to_pole_config.yaml`

Each one can be used like this:

```sh
python magnetopy.py diurnal-variation --config resources/config_templates/diurnal_variation_config.yaml
python magnetopy.py calculate-igrf --config resources/config_templates/calculate_igrf_config.yaml
python magnetopy.py plot-profile --config resources/config_templates/plot_profile_config.yaml
python magnetopy.py plot-map --config resources/config_templates/plot_map_config.yaml
python magnetopy.py reduction-to-pole --config resources/config_templates/reduction_to_pole_config.yaml
```

### YAML examples

#### diurnal-variation

```yaml
project_name: cerritos_test
stations_file: resources/data_examples/cerritos_datos_estaciones.csv
stations_cols: date,time,latitude,longitude,magnetic_field
base_station_file: resources/data_examples/cerritos_estaciones_base.csv
base_station_cols: date,time,magnetic_field
```

#### calculate-igrf

```yaml
project_name: cerritos_test
stations_file: resources/data_examples/cerritos_datos_estaciones.csv
stations_cols: date,time,gpslat,gpslon,magfield
altitude: 1.92
date: 2019-03-26
verbose: false
```

#### plot-profile

```yaml
project_file: resources/cerritos_test/cerritos_test_2026-05-08_223841.csv
col_to_plot: diurnal_var_corr
```

#### plot-map

```yaml
project_file: resources/cerritos_test/cerritos_test_2026-05-08_223841.csv
latitude_col: latitude
longitude_col: longitude
```

#### reduction-to-pole

```yaml
project_name: rtp_irregular
project_file: resources/data_examples/regular_grid.csv
easting_col: easting
northing_col: northing
magnetic_field_col: magnetic_field
inclination: 45.0
declination: -10.0
magnetization_inclination: 45.0
magnetization_declination: -10.0
upward_col: upward
# equivalent_sources: true
```

You can also override a config value on the command line. For example:

```sh
python magnetopy.py calculate-igrf --config resources/config_templates/calculate_igrf_config.yaml --date 2020-01-15
```

This keeps the rest of the configuration file as a reusable base while changing only the arguments you need for a single run.

---