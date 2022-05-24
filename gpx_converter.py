import gpxpy
import pandas as pd
from utils import *

"""
################### GPX TO CSV CONVERTER ##################
##                                                       ##  
##  Written by Juan Carlos Bucio (jcbucio.geo@gmail.com) ##
##               Licensed under MIT license              ##
##                                                       ##
###########################################################

Run this script to convert a gpx file to a csv file

usage: gpx_convert.py [-h]

optional arguments:
    -h, --help      show this help message and exit
"""

try:
    input_file = str(input("GPX file path and name: "))
    gpx_file = open(input_file, 'r')
    gpx = gpxpy.parse(gpx_file)
except:
    print('\n--- ERROR: No gpx file was found ---\n')
    exit()

output_file = str(input("CSV output file path and name: "))

df = pd.DataFrame(columns=['route', 'station', 'latitude', 'longitude'])

try:
    for route in gpx.routes:
        for point in route.points:
            df.loc[point, 'route'] = route.name
            df.loc[point, 'station'] = point.name
            df.loc[point, 'latitude'] = point.latitude
            df.loc[point, 'longitude'] = point.longitude
except:
    print('\n--- ERROR: The format data in the gpx file is not supported ---\n')
    exit()

df['route'] = df['route'].apply(lambda x: format_route(x))
df['station'] = df['station'].apply(lambda x: format_station(x))

df.to_csv(output_file, index=False)
print("\nData saved in: " + output_file + "\n")