# How to use MagnetoPy

---
## Environment manual
You can review the [ENVIRONMENT_MANUAL.md][environment_manual] file in the MagnetoPy documentation to prepare your project.

---
## Get help
MagnetoPy help:

    --help

```sh
python <repository_path>\magnetopy\src\magnetopy\magnetopy_cli\magnetopy.py --help
```

Help by command:

    diurnal-variation --help

```sh
python <repository_path>\magnetopy\src\magnetopy\magnetopy_cli\magnetopy.py <command> --help
```

---
## Available commands in magnetopy-cli
    Commands: diurnal-variation, calculate-igrf, reduction-to-pole.

___
### diurnal-variation
    Command: diurnal-variation [options]

    MagnetoPy command that calculate the diurnal variation using field data and base station registers.

    --stations_file <value>         Stations file path containing date, time, magfield, latitude and longitude data of the study (required).
    --stations_cols <value>         Stations file columns names in the following order: date, time, magfield, latitude and longitude (required).
    --base_station_file <value>     Base station file path containing date, time and magfield of the study (required).
    --base_stations_cols <value>    Base station columns names in the following order: date, time and magfield (required).

___
### calculate-igrf
    Command: calculate-igrf [options]

    MagnetoPy command that calculate the total magnetic field intensity from the IGRF coefficients using field data and base stations.

    --stations_file <value>         Stations file path containing date, time, magfield, latitude and longitude data of the study (required).
    --stations_cols <value>         Stations file columns names in the following order: date, time, magfield, latitude and longitude (required).
    
___
### reduction-to-pole
    Command: reduction-to-pole [options]

    MagnetoPy command that compute the reduction to the pole of magnetic data using frequency domain calculations through Fast Fourier Transform.

___
### Further information
If there are still some doubts about the usage of these commands, you can check the video tutorials on the MagnetoPy's series in Youtube:
[MagnetoPy - ¿Cómo usar?](https://jcbucio.github.io/portafolio/MagnetoPy)