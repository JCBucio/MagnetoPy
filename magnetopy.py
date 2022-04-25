import argparse
import pandas as pd
import numpy as np
from utils import *
import time
import requests

"""
Run this script to obtain the magnetic field data per station from a base stations
and save the data in a csv file that contains the corrections needed. Aditionally, 
the script can request the IGRF data for every point in our stations and base files.

usage: magnetopy.py [-h] stationsfile basefile outputfile

positional arguments:
    stationsfile    name of the file with the stations data
    basefile        name of the file with the base stations data
    outputfile      name of the file with the output data

optional arguments:
    -h, --help      show this help message and exit
"""

intro = '''
############## MAGNETIC FIELD DATA FORMATTER ##############
##                                                       ##  
##  Written by Juan Carlos Bucio (jcbucio.geo@gmail.com) ##
##               Licensed under MIT license              ##
##                                                       ##
###########################################################
'''
print(intro)

t = time.time()

parser = argparse.ArgumentParser(description='Magnetic Field Data Formatter')
parser.add_argument('stationsfile', type=str, help='Enter the name of the stations file with extension')
parser.add_argument('basefile', type=str, help='Enter the name of the base stations file with extension')
parser.add_argument('outputfile', type=str, help='Enter the name of the output file with extension')
args = parser.parse_args()

try:
    sta_file = args.stationsfile
    sta_file = pd.read_csv(sta_file)
except:
    print('\n--- ERROR: No stations file was entered ---\n')
    exit()

try:
    base_file = args.basefile
    base_file = pd.read_csv(base_file)
except:
    print('\n--- ERROR: No base stations file was entered ---\n')
    exit()

try:
    out_file = args.outputfile
except:
    print('\n--- ERROR: No output file was entered ---\n')
    exit()


##################################### STATION FILE COLUMNS #####################################
print('\n--- STATIONS FILE PARAMETERS ---\n')
print('Enter the columns names of the file')
sta_date = str(input("Date column: "))
sta_time = str(input("Time column: "))
sta_station = str(input("Stations column: "))
sta_field = str(input("Magnetic field column: "))
sta_lat = str(input("Latitude column: "))
sta_lon = str(input("Longitude column: "))

# Check that the columns exist
try:
    sta_file = sta_file[[sta_date, sta_time, sta_station, sta_field, sta_lat, sta_lon]]
    print('\nColumns found!\n')
except:
    print('\n--- ERROR: Some columns were not found, check your columns names ---\n')
    exit()

# Change the columns names
sta_file.columns = ['sta_date', 'sta_time', 'station', 'sta_field', 'sta_lat', 'sta_lon']

# Check that the time and date formats are correct
sta_file['sta_time'] = sta_file['sta_time'].apply(lambda x: format_time(x))
# sta_file['sta_date'] = sta_file['sta_date'].apply(lambda x: format_date(x))


##################################### STATION FILE COLUMNS #####################################
print('\n--- BASE STATIONS FILE PARAMETERS ---\n')
print('Enter the columns names of the file')

# base_date = str(input("Date of your data in DD/MM/YYYY format: "))
# try:
#     check_date = base_date.split('/')
#     if len(check_date) == 3:
#         if len(check_date[0]) == 2 and len(check_date[1]) == 2 and len(check_date[2]) == 4:
#             print('\nThe date format is correct!\n')
#         else:
#             print('\n--- ERROR: Date format incorrect! ---\n')
#             exit()
#     else:
#         print('\n--- ERROR: Date format incorrect! ---\n')
#         exit()
# except:
#     print('\n--- ERROR: Date format incorrect! ---\n')
#     exit()

base_date = str(input("Date column: "))
base_time = str(input("Time column: "))
base_field = str(input("Magnetic field column: "))
base_sq = str(input("Resolution column: "))

# Check that the columns exist
try:
    base_file = base_file[[base_date, base_time, base_field, base_sq]]
    print('\nColumns found!\n')
except:
    print('\n--- ERROR: Some columns were not found, check your columns names ---\n')
    exit()

base_file.columns = ['base_date', 'base_time', 'base_magfield', 'base_sq']

# Check that the time and date formats are correct
base_file['base_time'] = base_file['base_time'].apply(lambda x: format_time(x))
# base_file['base_date'] = base_file['base_date'].apply(lambda x: format_date(x))

######################## FINAL DATA PROCESSING ########################
print('Finding closest matches in time of base stations...')
final_data = sta_file.copy()
final_data.columns = ['sta_date', 'sta_time', 'station', 'sta_magfield', 'gps_lat', 'gps_lon']
base_file.insert(0, 'diff_time', np.nan)
base_cols = base_file.columns
final_data = final_data.assign(**dict.fromkeys(base_cols, np.nan))

for i in range(len(final_data)):
    for date in base_file['base_date']:
        if final_data['sta_date'][i] == date:
            # Select the data from base_file that has the same date
            base_file_date = base_file[base_file['base_date'] == date]
            closest_time = base_file_date.iloc[np.argmin(np.abs(base_file_date['base_time'] - final_data.loc[i, 'sta_time'])), :]
            final_data.loc[i, 'base_date'] = closest_time['base_date']
            final_data.loc[i, 'base_time'] = closest_time['base_time']
            final_data.loc[i, 'base_magfield'] = closest_time['base_magfield']
            final_data.loc[i, 'base_sq'] = closest_time['base_sq']
            final_data.loc[i, 'diff_time'] = final_data.loc[i, 'sta_time'] - final_data.loc[i, 'base_time']
            final_data.loc[i, 'base_magfield_mean'] = np.mean(base_file_date['base_magfield'])


######################## DAY VARIATION PROCESSING ########################
# base_mean_magfield = base_file['base_magfield'].mean()
final_data['diurnal_var'] = final_data['base_magfield'] - final_data['base_magfield_mean']
final_data['diurnal_var_corr'] = final_data['sta_magfield'] - final_data['diurnal_var']

print('\nData matching and correction for diurnal variation completed!\n')

final_data.to_csv(out_file, index=False, sep=',', encoding='utf-8')

######################## IGRF API REQUEST ########################
try:
    print('\nRequesting IGRF data...\n')
    api_url = 'https://www.ngdc.noaa.gov/geomag-web/calculators/calculateIgrfwmm'
    requests_time = time.time()
    req_number = 0
    # Loop through the data and request the IGRF data
    for i in range(len(final_data)):
        req_number += 1

        date = final_data['base_date'][i]
        day, month, year = date.split('/')

        # Set the parameters for the request
        params = {
            'lat1': final_data['gps_lat'][i],
            'lon1': final_data['gps_lon'][i],
            'coordinateSystem': 'D',
            'model': 'IGRF',
            'startYear': int(year),
            'startMonth': int(month),
            'startDay': int(day),
            'endYear': int(year),
            'endMonth': int(month),
            'endDay': int(day),
            'resultFormat': 'json'
        }
        # Request the data
        response = requests.get(api_url, params=params)
        # Check if the request was successful and print the number of the request every 10 requests
        if response.status_code == 200:
            if req_number % 10 == 0:
                print('{} requests completed...'.format(req_number))
                time.sleep(1)
        else:
            print('\n--- ERROR: Request #{} failed! ---\n'.format(req_number))
            exit()

        # Add the response data to the final_data dataframe
        response = response.json()
        igrf_intensity = response['result'][0]['totalintensity']
        final_data.loc[i, 'igrf_intensity'] = igrf_intensity


    print('\n{} requests completed in {} minutes\n'.format(req_number, "{:.3f}".format((time.time() - requests_time)/60)))

except:
    print('\n--- ERROR: IGRF service is not available ---\n')
    print('Data succesfully saved without IGRF correction in: ' + out_file)
    print('\nTotal time spent: {} minutes\n'.format("{:.3f}".format((time.time() - t)/60)))
    exit()

######################## IGRF CORRECTION ########################
final_data['igrf_res_field'] = final_data['diurnal_var_corr'] - final_data['igrf_intensity']

######################## OUTPUT ########################
print('\n--- OUTPUT FILE ---\n')

final_data.to_csv(out_file, index=False, sep=',', encoding='utf-8')

print('Data succesfully saved in: ' + out_file)
print('\nTotal time spent: {} minutes\n'.format("{:.3f}".format((time.time() - t)/60)))