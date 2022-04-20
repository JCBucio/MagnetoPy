import argparse
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

usage: gpx_convert.py [-h] gpx_file csv_file

positional arguments:
    gpx_file    name of the gpx file
    csv_file    name of the output csv file

optional arguments:
    -h, --help      show this help message and exit
"""

parser = argparse.ArgumentParser(description='GPX to CSV Converter')
parser.add_argument('gpx_file', type=str, help='Enter the name of the gpx file with extension')
parser.add_argument('csv_file', type=str, help='Enter the name of the output csv file with extension')
args = parser.parse_args()

try:
    gpx_file = open(args.gpx_file, 'r')
    gpx = gpxpy.parse(gpx_file)
except:
    print('\n--- ERROR: No gpx file was found ---\n')
    exit()

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

df.to_csv(args.csv_file, index=False)
print("\nData saved in: " + args.csv_file + "\n")