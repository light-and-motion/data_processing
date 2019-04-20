import user_interface
import numpy as np
import pandas as pd
from data_processing import Data_Processing
from win32com.client import Dispatch

### Main execution block ###
user_interface.banner()

#Asks user for which type of data to process based on numeric input. To be passed into choose_config
data_choice = None
while data_choice == None:
    print('Which data file type would you like to process?\n1. Lumensphere\n2. Multimeter\n3. Serial Data\n')
    data_choice = int(input('Enter a number: '))

config_list = user_interface.choose_config(data_choice)
config_file = config_list[0]
config_title = config_list[1]
input_csv = user_interface.choose_csv()
output_name = user_interface.choose_output_name()

df = Data_Processing(data_choice, config_file, input_csv, output_name)


# Get the names of the columns and read the configuration file into config_df_1
# Then conver the column inputs and outputs into integers and titles to later use as indices 
config_df_1 = df.create_excel_dataframe(config_title, config_file.sheetnames[0])


config_df_2 = df.create_excel_dataframe(config_title, config_file.sheetnames[1])


# Reset config_df_2['Header'] so that it only stores non-NaN values and resets the index 
'''
config_df_2['Header'].dropna(inplace=True)
config_df_2['Header'].reset_index(drop=True, inplace = True)
print(config_df_2['Header'])
# Retrieve the csv file and store its contents into a dataframe 

'''
raw_data_df = df.create_csv_dataframe(input_csv, config_df_2['Start Row'].loc[0])

# Read the raw dataframe into an Excel file 
raw_data_excel = df.create_raw_Excelbook(raw_data_df)

col_names = raw_data_df.columns
config_df_1 = df.convert_columns(config_df_1, col_names)
#print(config_df_1)

# mapping_data_df will hold all the columns that we want to plot later

# We will use col_titles_inputs as indices to extract from the raw data the columns that we want plotted
# Note: Even though only one column is being extracted at a time, the column being extracted 
# is stored in a dataframe as only dataframes, not series!, can combine with other dataframes. 


## Do range slicing here 
mapping_data_df = df.create_mapping_dataframe(raw_data_df, config_df_1['Input'], config_df_1['Range'])
# format time only if the time columns is to be mapped
new_titles = config_df_1['Input']

time_col = config_df_2['Time Axis']

# Store the new time col in a new Series temporarily, 
# so the NaNs in mapping_data[time_title] won't convert
# the data type into object. 
if (not time_col.dropna().empty): 
    # Retrieve the column title of the 'time' column 
    time_unit = config_df_2['Time Unit'].loc[0]
    time_index = df.letter2int(config_df_2['Time Axis']).loc[0]
    time_title = raw_data_df.columns[time_index-1]

    # Retrieve the start time and convert it to a string in elapsed time format 
    # start_time is a Series with length 1 
    start_time = pd.Series(raw_data_df[time_title].loc[0])
    start_time = df.convert_to_time_object(start_time, time_unit)


    new_time_col = pd.DataFrame()
    new_time_col = df.convert_to_time_object(mapping_data_df[time_title], time_unit)
    df.time_format(new_time_col, start_time.loc[0])
    #df.time_format(mapping_data_df[time_title])
print("After formatting time")
mapping_data_df[time_title] = new_time_col



# Output files 
excel_output = config_df_2['Excel'].loc[0]
jpeg_output = config_df_2['JPEG'].loc[0]

# Grab the x-axis and y-axis and determine if a chart will be outputted 
axis = df.make_chart(config_df_1['Axis'])
x_axis = axis[0]
y_axis = axis[1]
create_chart = False
if (x_axis.size != 0 and y_axis.size != 0): 
    create_chart = True

# Creating an Excel file 
if (excel_output == 'YES' or pd.isnull(excel_output)):
    # create workbook to hold plotted data
    output_data_wb = df.create_plotted_workbook()

    # Read the output data into an Excel file
    output_data_wb = df.process_data(output_data_wb, mapping_data_df, config_df_1)

    # If the x_axis is not empty, then create a chart 
    if (create_chart): 
        df.create_chart(output_data_wb, mapping_data_df, x_axis, y_axis, config_df_1, config_df_2)

    #print(df.get_output_name)
    output_data_wb.save(df.get_output_name + '.xlsx')

# create the jpg file 
if (pd.isnull(jpeg_output) or jpeg_output.upper() == 'YES' or create_chart):
    df.make_jpeg(mapping_data_df, x_axis, y_axis, config_df_1, config_df_2, output_name)



