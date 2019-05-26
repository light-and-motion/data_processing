from datetime import datetime
import pandas as pd
import numpy as np

def search_for_military_times(df): 
        datetime_str_column = []
        i = 0
        for column in df: 
            series = df[column]
            for format in ('%m/%d/%Y %H:%M', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S.%f'): 
                datetime_str = str(series.loc[0])
                try: 
                    datetime.strptime(datetime_str, format)
                    datetime_str_column.append(column)
                except ValueError: 
                    continue
                i += 1
    
        return datetime_str_column

def date_parser(datetime_str_series) -> pd.Series:
        """Converts a series that holds string representations of military time into 
        a series that holds string representations of standard time.   
         
        Parameters
        ---------- 
        datetime_str_series : pd.Series
            Contains military times 
        """

        # Drop empty columns so you don't get an index out of range error 
        datetime_str_pm = datetime_str_series.replace('', np.nan).dropna()
        
        period = 'AM'
        for datetime_str in datetime_str_pm:  
            
            datetime_str_list = datetime_str.split()
            date = datetime_str_list[0]
            time = datetime_str_list[1]
            time_list = time.split(':')
            
            # Grab the hours
            hours = int(time_list[0])
            if (hours == 12): 
                period = 'PM'
            if (hours > 12): 
                hours = str(hours-12)
            
            # Grab the minutes
            minutes = time_list[1]

            # Grab the seconds 
            if (len(time_list) == 3): 
                seconds = time_list[2]
            else: 
                seconds = '00'
            
            # Replace
            new_str = date + ' ' + str(hours) + ':' +  minutes + ':' +  seconds + ' ' + period  
            datetime_str_series.replace(datetime_str, new_str, inplace=True)
        return datetime_str_series
    
# df = pd.read_csv('test_datetime_microseconds.csv')
# # date_parser(df['StartTime1'])
# print(date_parser(df['StartTime1']))
