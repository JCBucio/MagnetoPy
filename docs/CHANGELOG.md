# Change Log
Project change history.

---

## Versioning convention

MagnetoPy follows a semantic versioning model based on the format `X.Y.Z`.

- `X` = major version. Indicates a major update to the tool, such as adding a new command, changing the workflow, or updating critical libraries that affect the tool's proper functioning.
- `Y` = minor version. Indicates a moderate update, such as adding a new test, updating documentation, adding usage examples, or introducing a small but meaningful feature that does not drastically change the core workflow.
- `Z` = patch/minor maintenance version. Indicates a minimal update, such as code reformatting, log changes, internal cleanup, or other modifications that do not directly affect the tool's workflow.

This convention helps users quickly understand the impact of each release and whether a new version may require changes in how they use the tool.

---

## MagnetoPy ```1.0.0```(May 6th, 2024)

First stable version of MagnetoPy


| **Command**                | **Calculation**                             |**Status**                                   |
|----------------------------|---------------------------------------------|---------------------------------------------|
| diurnal-variation	         | Diurnal variation calculation               | Available                                   |
| calculate-igrf	         | IGRF Coefficients calculation               | In development                              |
| reduction-to-pole          | Reduction to Pole calculation               | In development                              |

## MagnetoPy ```1.1.0``` (June 22nd, 2024)

New features:

- Added `calculate-igrf` command to calculate IGRF coefficients.

Tests:

- Added unit test for the `diurnal-variation` command.

Documentation:

- Added documentation for the `calculate-igrf` command in the HOW_TO_USE.md file.

| **Command**                | **Calculation**                             |**Status**                                   |
|----------------------------|---------------------------------------------|---------------------------------------------|
| diurnal-variation	         | Diurnal variation calculation               | Available                                   |
| calculate-igrf	         | IGRF Coefficients calculation               | **Available**                               |
| reduction-to-pole          | Reduction to Pole calculation               | In development                              |

## MagnetoPy ```1.2.0``` (August 7th, 2024)

New features:

- Added `plot-profile` command to plot the profile of a selected column in the data.

Documentation:

- Added documentation for the `plot-profile` command in the HOW_TO_USE.md file.

| **Command**                | **Calculation**                             |**Status**                                   |
|----------------------------|---------------------------------------------|---------------------------------------------|
| diurnal-variation	         | Diurnal variation calculation               | Available                                   |
| calculate-igrf	         | IGRF Coefficients calculation               | Available                                   |
| reduction-to-pole          | Reduction to Pole calculation               | In development                              |
| plot-profile               | Plot profile of a selected column           | **Available**                               |

## MagnetoPy ```1.2.1``` (May 8th, 2026)

New features:

- Added unit tests for the `calculate-igrf` command.
- Updated IGRF coefficients to the latest version (IGRF-14).

Documentation:

- Updated documentation for the `calculate-igrf` command.

| **Command**                | **Calculation**                             |**Status**                                   |
|----------------------------|---------------------------------------------|---------------------------------------------|
| diurnal-variation	         | Diurnal variation calculation               | Available                                   |
| calculate-igrf	         | IGRF Coefficients calculation               | Available                                   |
| reduction-to-pole          | Reduction to Pole calculation               | In development                              |
| plot-profile               | Plot profile of a selected column           | Available                                   |

## MagnetoPy ```1.2.2``` (August 29th, 2026)

New features:

- Added `plot-map` command to visualise geographic locations of magnetic data points from CSV files.

Documentation:

- Added documentation for the `plot-map` command in the HOW_TO_USE.md file.

| **Command**                | **Calculation**                             |**Status**                                   |
|----------------------------|---------------------------------------------|---------------------------------------------|
| diurnal-variation	         | Diurnal variation calculation               | Available                                   |
| calculate-igrf	         | IGRF Coefficients calculation               | Available                                   |
| reduction-to-pole          | Reduction to Pole calculation               | In development                              |
| plot-profile               | Plot profile of a selected column           | Available                                   |
| plot-map                  | Plot geographic locations of data points    | Available                                   |

## MagnetoPy ```2.0.0``` (October 4th, 2026)

New features:

- Added `reduction-to-pole` command as an available workflow for magnetic data processing.
- Added support for config files so commands can be configured through JSON, YAML/YML, or INI files.
- Added the `--verbose` option to the `calculate-igrf` command to include secular variation columns in the output CSV.
- Improved the CLI usage workflow by making config files the preferred method and keeping CLI arguments as a targeted override option.

Documentation:

- Updated `ENVIRONMENT_MANUAL.md` to document the Conda-based environment setup.
- Updated `HOW_TO_USE.md` with config-file examples and command usage notes.
- Updated `README.md` with the Conda quick-start flow and config-first examples.
- Added a new `FAQ.md` file with usage tips and troubleshooting guidance.

| **Command**                | **Calculation**                             |**Status**                                   |
|----------------------------|---------------------------------------------|---------------------------------------------|
| diurnal-variation	         | Diurnal variation calculation               | Available                                   |
| calculate-igrf	         | IGRF Coefficients calculation               | Available                                   |
| reduction-to-pole          | Reduction to Pole calculation               | **Available**                               |
| plot-profile               | Plot profile of a selected column           | Available                                   |
| plot-map                  | Plot geographic locations of data points    | Available                                   |