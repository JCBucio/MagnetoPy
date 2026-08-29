# MagnetoPy AI Coding Agent Instructions

## Project Overview
MagnetoPy is a geophysics-focused Python CLI tool for processing magnetic field data. It performs specialized calculations including diurnal variation correction, IGRF-14 geomagnetic reference field calculations, and data visualization. The codebase emphasizes data validation, geospatial calculations, and scientific accuracy over performance optimization.

## Architecture & Major Components

### CLI-Command Dispatch Pattern
- **Entry point**: [magnetopy.py](../magnetopy.py) creates a `Magnetopy` class that orchestrates the command flow
- **Command routing**: [magnetopy_cli/magnetopy_parser.py](../src/magnetopy/magnetopy_cli/magnetopy_parser.py) defines subcommands (`diurnal-variation`, `calculate-igrf`, `plot-profile`, `reduction-to-pole`)
- **Command processors**: Each command (e.g., [DiurnalVariation](../src/magnetopy/magnetopy_core/diurnal_variation.py)) receives `Namespace` args and handles the computation independently

### Core Module (`magnetopy_core/`)
Three main command handlers inherit a similar pattern:
1. Parse arguments from CLI parser
2. Validate input files and column names via `MagnetoPyFilesHelper`
3. Perform domain-specific calculations
4. Save results using `MagnetoPyFilesHelper.save_data()`

**Key classes**:
- [DiurnalVariation](../src/magnetopy/magnetopy_core/diurnal_variation.py): Subtracts base station variations from field measurements
- [CalculateIGRF](../src/magnetopy/magnetopy_core/calculate_igrf.py): Computes geomagnetic components using IGRF-14 coefficients via `MagnetoPyIGRFHelper`
- [PlotProfile](../src/magnetopy/magnetopy_core/plot_profile.py): Matplotlib-based visualization

### Utilities Layer (`magnetopy_utils/`)
**Stateless helper classes** (all methods are `@staticmethod`):
- [magnetopy_files_helper.py](../src/magnetopy/magnetopy_utils/magnetopy_files_helper.py): File I/O, date/time validation (flexible multi-format support), column verification, geospatial bounds checking
- [magnetopy_igrf_helper.py](../src/magnetopy/magnetopy_utils/magnetopy_igrf_helper.py): IGRF coefficient loading, spherical harmonic synthesis, coordinate transformations (geodetic ↔ geocentric)
- [magnetopy_conversions_helper.py](../src/magnetopy/magnetopy_utils/magnetopy_conversions_helper.py): Date-to-decimal-date conversion, coordinate system conversions
- [magnetopy_logging.py](../src/magnetopy/magnetopy_utils/magnetopy_logging.py): Color-coded console logging with consistent formatting

## Key Development Patterns

### Logging
Every class should create a logger on init:
```python
from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging
self.__magnetopy_logging = MagnetopyLogging().create_magnetopy_logging(logger='ClassName')
```
Use `logger.info()` for user feedback; logs include timestamps, file names, and line numbers.

### Data Validation
- Accept flexible date/time formats; see date validation in [magnetopy_files_helper.py](../src/magnetopy/magnetopy_utils/magnetopy_files_helper.py) for the precedent
- Validate geospatial bounds (latitude [-90, 90], longitude convention-dependent) before processing
- Verify CSV column presence and type before operations

### File Naming Conventions
- Output CSV files are named with timestamps: `{project_name}_YYYY-MM-DD_HHMMSS.csv`
- Helper method: [MagnetoPyFilesHelper.save_data()](../src/magnetopy/magnetopy_utils/magnetopy_files_helper.py)
- IGRF coefficients stored as SHC format in `resources/igrf{version}/`

### Dataframe Operations
- Rename columns internally using [MagnetoPyFilesHelper.rename_columns()](../src/magnetopy/magnetopy_utils/magnetopy_files_helper.py) to standardize prefixes (`sta_`, `base_`)
- Use pandas for all data manipulation; scipy.interpolate for coefficient interpolation
- Always reset index after concatenations/groupby: `df.reset_index(drop=True)`

## CLI Usage Examples

### Get Help
```bash
python magnetopy.py --help
python magnetopy.py diurnal-variation --help
python magnetopy.py calculate-igrf --help
python magnetopy.py plot-profile --help
```

### Diurnal Variation Correction
```bash
python magnetopy.py diurnal-variation \
  --project_name cerritos_test \
  --stations_file resources/data_examples/cerritos_datos_estaciones.csv \
  --stations_cols date,time,latitude,longitude,magnetic_field \
  --base_station_file resources/data_examples/cerritos_estaciones_base.csv \
  --base_station_cols date,time,magnetic_field
```
Outputs: `resources/cerritos_test/cerritos_test_YYYY-MM-DD_HHMMSS.csv`

### IGRF-14 Correction
```bash
python magnetopy.py calculate-igrf \
  --project_name cerritos_test \
  --stations_file resources/data_examples/cerritos_datos_estaciones.csv \
  --stations_cols date,time,gpslat,gpslon,magfield \
  --altitude 1.920 \
  --date 2019-03-26
```
Outputs: `resources/cerritos_test/cerritos_test_YYYY-MM-DD_HHMMSS.csv` with IGRF components (D, I, H, F, X, Y, Z, SV_*)

### Plot Profile
```bash
python magnetopy.py plot-profile \
  --project_file resources/cerritos_test/cerritos_test_2026-05-08_223841.csv \
  --col_to_plot diurnal_var_corr
```
Outputs: PNG plot in the same directory as the project file

## Testing Strategy
- Located in `tests/src/magnetopy/` mirroring the source structure
- Test files compare generated output CSVs against reference files in `resources/data_examples/`
- Pattern: Use unittest framework, create `Namespace` objects for argument passing
- Run all tests: `python -m pytest tests/`
- Run specific test: `python -m pytest tests/src/magnetopy/core/test_magnetopy_diurnal_variation.py`
- Run with verbose output: `python -m pytest tests/ -v`
- Test data located in `resources/data_examples/` (input) and `resources/cerritos_test/` (test outputs)

## External Dependencies
- **numpy, scipy**: Numerical/spherical harmonic calculations
- **pandas**: CSV I/O and dataframe operations
- **matplotlib**: Plotting (required by plot-profile command)
- **Version constraints**: See [requirements.txt](../requirements.txt); intentionally bounded (e.g., `numpy>=2.1,<3`)

## Common Tasks

### Adding a New Command
1. Define argument structure in [MagnetopyParser](../src/magnetopy/magnetopy_cli/magnetopy_parser.py)
2. Create command handler class in `magnetopy_core/` accepting `Namespace` args
3. Add command routing in [Magnetopy.__magnetopy_flow()](../magnetopy.py)
4. Add test file in `tests/src/magnetopy/core/` using reference data

### Modifying Date/Time Handling
- Update format lists in date/time validation methods in [magnetopy_files_helper.py](../src/magnetopy/magnetopy_utils/magnetopy_files_helper.py)
- Always return standardized format (dates as `YYYY-MM-DD`, times as `HH:MM:SS`)

### Extending IGRF Calculations
- Add methods to [MagnetoPyIGRFHelper](../src/magnetopy/magnetopy_utils/magnetopy_igrf_helper.py)
- Load coefficients via the `load_igrf_coefficients()` method
- Test with data in `resources/data_examples/` or `resources/cerritos_test/`

### Debugging Common Issues
- **File not found**: Verify paths are absolute or relative to workspace root; check `most_recent_file()` regex for output file parsing
- **Column not found**: Column names are case-sensitive; verify exact spelling matches CSV header
- **Date/time validation fails**: Add new format to the list in [validate_date()](../src/magnetopy/magnetopy_utils/magnetopy_files_helper.py) or [validate_time()](../src/magnetopy/magnetopy_utils/magnetopy_files_helper.py)
- **IGRF coefficients missing**: Verify `resources/igrf13/IGRF13.shc` exists and contains SHC format data
- **Log output not appearing**: Check logger names match class name passed to `create_magnetopy_logging(logger='...')`

## Geophysics Context
- **Diurnal variation**: Systematic magnetic field change due to solar activity; corrected by comparing field station to nearby base station
- **IGRF**: International Geomagnetic Reference Field; provides main field model for removing background magnetism
- **Reduction to Pole (RTP)**: Frequency-domain processing to correct for magnetic latitude effects (in development)
- All magnetic intensity values in nanoTesla (nT); altitudes in kilometers; dates in decimal-year format for coefficient interpolation

## Gotchas & Common Mistakes
- IGRF path currently hardcoded to `resources/igrf13/` even though IGRF-14 is mentioned; update if adding version switching
- Column naming in CLI args is comma-separated without spaces (e.g., `date,time,latitude,longitude`)
- Latitude/colatitude conversions used interchangeably; watch for `colat = 90 - latitude`
- Pandas `.groupby().transform()` is preferred over loops for efficiency
- Always handle timezone-naive datetime objects (no explicit UTC conversion in current code)
