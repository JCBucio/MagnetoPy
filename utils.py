import pandas as pd
import numpy as np

# Function that formats the values of the time column
def format_time(val):
    try:
        if len(str(val)) != 6 | str(val).isdigit() == False:
            if '/' in str(val):
                time = str(val).split('/')
            elif '-' in str(val):
                time = str(val).split('-')
            elif ':' in str(val):
                time = str(val).split(':')
            elif ' ' in str(val):
                time = str(val).split(' ')
            elif '.' in str(val):
                time = str(val).split('.')
            else:
                print('\n--- ERROR: The time format is not correct ---\n')
                exit()

            if len(time) == 3:
                h = time[0]
                m = time[1]
                s = time[2]
                if len(h) == 2 & len(m) == 2 & len(s) == 2:
                    return int(h + m + s)
                else:
                    print('\n--- ERROR: The time format is not correct ---\n')
                    exit()
            else:
                print('\n--- ERROR: The time format is not correct ---\n')
                exit()
        else:
            return val
    except:
        print('\n--- ERROR: The time format is not correct ---\n')
        exit()


