# Frequently Asked Questions

---

## How do I run MagnetoPy?

MagnetoPy is designed as a fast, direct Command Line Interface. Most standard workflows can be run with single-line positional commands:

```sh
# 1. Diurnal variation correction
python magnetopy.py diurnal-variation survey.csv base.csv

# 2. IGRF-14 computation and residual magnetic anomaly
python magnetopy.py calculate-igrf survey_diurnal.csv --altitude 1.92

# 3. Plot survey points on a map
python magnetopy.py plot-map survey.csv

# 4. Plot profile of a column
python magnetopy.py plot-profile survey_diurnal.csv

# 5. Reduction to the Pole
python magnetopy.py reduction-to-pole grid.csv --inclination 45 --declination -10
```

---

## How does automatic column detection work?

MagnetoPy inspects your CSV file headers and automatically maps standard geophysical column names:

- **Date:** `date`, `fecha`, `dia`, `day`, `sta_date`, `base_date`
- **Time:** `time`, `hora`, `timestamp`, `time_utc`, `sta_time`, `base_time`
- **Coordinates (Latitude / Northing):** `latitude`, `lat`, `gpslat`, `northing`, `north`, `y`, `norte`
- **Coordinates (Longitude / Easting):** `longitude`, `lon`, `long`, `gpslon`, `easting`, `east`, `x`, `este`
- **Magnetic field:** `magfield`, `mag`, `magnetic_field`, `nT`, `total_field`, `field`, `f`, `campo`, `diurnal_var_corr`, `mag_anomaly(nT)`

If your CSV uses these standard names, you do not need to provide any column arguments.

---

## What if my column names are custom or unusual?

You can explicitly specify columns using command flags:

```sh
# Explicit columns for diurnal variation
python magnetopy.py diurnal-variation survey.csv base.csv \
    --stations_cols date,time,gps_latitude,gps_longitude,reading \
    --base_station_cols date,time,reading

# Explicit columns for plot-map
python magnetopy.py plot-map survey.csv --latitude_col custom_lat --longitude_col custom_lon
```

---

## What is the `mag_anomaly(nT)` column produced by `calculate-igrf`?

In geophysics, the primary objective of calculating the IGRF (International Geomagnetic Reference Field) is to remove Earth's core background field from the observed measurements to obtain the crustal magnetic anomaly:

$$\Delta T = T_{\text{observed}} - F_{\text{IGRF}}$$

The output CSV includes both the core model components (`D`, `I`, `H`, `F`, `X`, `Y`, `Z`) and `mag_anomaly(nT)`.

---

## Why do I get a "Missing required arguments" error?

This occurs when a strictly required argument is missing:

- For `diurnal-variation`: missing the stations survey file or base station file.
- For `calculate-igrf`: missing the stations file or `--altitude`.
- For `plot-map` / `plot-profile`: missing the input CSV file.
- For `reduction-to-pole`: missing `--inclination` or `--declination`.

Check the command help for details:

```sh
python magnetopy.py <command> --help
```

---

## Where are output files saved?

By default, output files are saved in the `resources/<project_name>/` directory:
- If `--project_name` is omitted, MagnetoPy automatically names the project after your input file.
- Plots are saved directly next to the input data file or in the project directory.

---
