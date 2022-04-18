# Function that formats the values of the time column
def format_time(val):
    try:
        if len(str(val)) != 6 or str(val).isdigit() == False:
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
                return int(val)

            if len(time) == 3:
                h = time[0]
                m = time[1]
                s = time[2]
                if len(h) == 2 and len(m) == 2 and len(s) == 2:
                    return int(h + m + s)
                else:
                    print('\n--- ERROR: The time format is not correct ---\n')
                    exit()
            else:
                print('\n--- ERROR: Check that your date format has hours, minutes and seconds ---\n')
                exit()
        else:
            return int(val)
    except:
        print('\n--- ERROR: The time format is not correct ---\n')
        exit()


# Function that formats the values of the date column
def format_date(value):
    try:
        # Strip the date of the spaces
        val = value.strip()

        if '/' in val:
            date = val.split('/')
        elif '-' in val:
            date = val.split('-')
        elif '.' in val:
            date = val.split('.')
        else:
            print('\n--- ERROR: Incorrect date format ---\n')
            return val

        if len(date) == 3:
            d = date[0]
            m = date[1]
            y = date[2]
            if len(d) == 2 and len(m) == 2 and len(y) == 4:
                str_date = str(d) + '/' + str(m) + '/' + str(y)
                return str_date
            else:
                print('\n--- ERROR: Make sure that your date is in the following format: DD/MM/YYYY ---\n')
                return val
        else:
            print("\n--- ERROR: Check that your date format has any separator of the following: '/', '-', '.'. ---\n")
            return val
    except Exception as e:
        print(e)
        print('\n--- ERROR: The date format could not be processed ---\n')
        exit()