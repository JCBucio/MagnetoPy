# Frequently Asked Questions

---

## Why should I use a config file instead of typing all parameters directly?

MagnetoPy commands often include long paths, repeated column names, and project-specific values. A config file keeps all of that in one place and makes the workflow easier to reproduce.

Preferred usage:

```sh
python magnetopy.py calculate-igrf --config resources/config_templates/calculate_igrf_config.yaml
```

This is especially helpful when you are working with multiple projects or repeated processing runs.

---

## What is the parameter priority in MagnetoPy?

The priority is:

1. Config file values
2. CLI arguments

Use the config file as the main source of project settings and use CLI arguments only to override a single value for a specific run.

Example:

```sh
python magnetopy.py calculate-igrf --config resources/config_templates/calculate_igrf_config.yaml --date 2020-01-15
```

This keeps the rest of the configuration fixed while changing only the date.

---

## Which file formats are supported for config files?

MagnetoPy accepts JSON, YAML/YML, and INI config files.

Examples:

```yaml
project_name: cerritos_test
stations_file: resources/data_examples/cerritos_datos_estaciones.csv
stations_cols: date,time,gpslat,gpslon,magfield
altitude: 1.92
date: 2019-03-26
```

---

## How do I know which columns to pass in `--stations_cols` or `--base_station_cols`?

The order matters. The tool expects the exact order of the columns, and the values must match the columns in the CSV file.

For example:

```sh
--stations_cols date,time,latitude,longitude,magnetic_field
--base_station_cols date,time,magnetic_field
```

If your CSV header names differ, use the actual column names from the file.

---

## Why do I get a "Missing required arguments" error?

This usually means one or more required values are missing from the config file or were not provided on the command line.

Common examples:

- missing `project_name`
- missing `stations_file`
- missing `stations_cols`
- missing `altitude` for `calculate-igrf`
- missing `project_file` for `plot-profile` or `plot-map`

Check the command help:

```sh
python magnetopy.py <command> --help
```

---

## Why do I get a file not found error?

This usually happens because the path is wrong or the file is not relative to the project root.

Use absolute paths or paths relative to the project root, for example:

```sh
resources/data_examples/cerritos_datos_estaciones.csv
```

or:

```sh
/home/user/MagnetoPy/resources/data_examples/cerritos_datos_estaciones.csv
```

---

## How do I run a command from the terminal?

Use the entry point script at the project root:

```sh
python magnetopy.py --help
python magnetopy.py calculate-igrf --config resources/config_templates/calculate_igrf_config.yaml
```

If you are using Conda, first activate your environment:

```sh
conda activate magnetopy_env
```

---

## What should I do if a plot command does not create the image?

Check that:

- the input CSV exists
- the file path is correct
- the column names used in the config or CLI match the CSV headers
- the command is run from the project root

Example:

```sh
python magnetopy.py plot-profile --config resources/config_templates/plot_profile_config.yaml
```

---

## What is the recommended workflow for a new project?

1. Copy one of the sample config files from `resources/config_templates/`
2. Edit the paths and column names for your project
3. Run the command with `--config`
4. Override only the values you need for a single run

This is the simplest and most reproducible workflow for MagnetoPy.

---

## Do I need to type everything manually each time?

No. In most cases, you should keep a YAML config file per project and run:

```sh
python magnetopy.py <command> --config path/to/config.yaml
```

This keeps the workflow fast, readable, and easier to track.

---

## Can I reuse the same config for multiple runs?

Yes. That is one of the advantages of the config-file approach. You can keep a stable project configuration and change only a few values when needed.

---

## Where can I find example configuration files?

The repository includes templates in:

```text
resources/config_templates/
```

Examples:

- `diurnal_variation_config.yaml`
- `calculate_igrf_config.yaml`
- `plot_profile_config.yaml`
- `plot_map_config.yaml`
- `reduction_to_pole_config.yaml`

---

## What if I want to inspect the available options for a command?

Use:

```sh
python magnetopy.py <command> --help
```

This is useful when you are unsure about required arguments or expected option names.

---

## Why do my column names sometimes look different from the examples?

CSV headers can vary between datasets. MagnetoPy expects the exact names you pass in `--stations_cols`, `--base_station_cols`, `--latitude_col`, `--longitude_col`, and similar arguments.

If the columns differ, update the config file to match the real header names.

---

## Is the CLI still available?

Yes. The CLI remains available, but the recommended workflow is to define the main project configuration in a config file and use CLI arguments only for quick overrides.

---
