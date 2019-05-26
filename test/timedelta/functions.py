import pandas as pd
import numpy as np 

def test_init(): 
    print('Hello World')
    
def to_timedelta(df): 
    df['Elapsed Time'] = pd.to_timedelta(df['ElapsedTime'])
    return df

def to_str(df): 
    df['ElapsedTime'] = df['ElapsedTime'].astype(str)
    df['ElapsedTime'] = [date[-8:] for date in df['ElapsedTime']]
    return df

def timedelta_to_string(config, df): 
    df = df.fillna('')
    indices = config['Time Unit'].dropna().index

    for i in indices: 
        label = config['Title'].loc[i]
        df[label] = [time[7:15] for time in df[label].astype(str)]
    return df['ElapsedTime']

# if __name__ == '__main__': 
#     df = pd.read_csv('test_datetime_to_string.csv')
#     df['ElapsedTime'] = pd.to_timedelta(df['ElapsedTime'])
#     config = pd.read_excel('Config.xlsx')
#     # print(to_str(df))
#     print(df)
#     print(timedelta_to_string(config, df))
    
    