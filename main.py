import user_interface
from data_processing import Data_Processing

### Main execution block ###
user_interface.banner()

#Asks user for which type of data to process based on numeric input. To be passed into choose_config
data_choice = None
while data_choice == None:
    print('Which data file type would you like to process?\n1. Lumensphere\n2. Multimeter\n3. Serial Data\n')
    data_choice = int(input('Enter a number: '))

config_file = user_interface.choose_config(data_choice)
input_csv = user_interface.choose_csv()
output_wb = user_interface.choose_output_wb()

df = Data_Processing(data_choice, config_file, input_csv, output_wb)


# Retrieve the csv file and store its contents into a dataframe 
raw_data_df = df.create_csv_dataframe(input_csv)

# Read the raw dataframe into an Excel file 
raw_data_excel = df.create_raw_Excelbook(raw_data_df)


# Get the names of the columns and read the configuration file into config_df
# Then conver the column inputs and outputs into integers and titles to later use as indices 
col_names = raw_data_df.columns
config_df = df.create_excel_dataframe(config_file)
config_df = df.convert_columns(config_df, col_names)

# output_data_df will hold all the columns that we want to plot later

# We will use col_titles_inputs as indices to extract from the raw data the columns that we want plotted
# Note: Even though only one column is being extracted at a time, the column being extracted 
# is stored in a dataframe as only dataframes, not series!, can combine with other dataframes. 

output_data_df = df.create_output_dataframe(raw_data_df, config_df['Input Column Title'])


# format time 
output_data_df['Date/Time'] = df.time_format(output_data_df['Date/Time']) 


# create workbook to hold plotted data
output_data_wb = df.create_plotted_workbook()


# Read the output data into an Excel file
output_data_wb = df. process_data(output_data_wb, output_data_df, config_df)


##### Chart creation 

# Call make_chart() to determine if we need to create a chart 
axis = config_df['Axis']
x_axis = df.make_chart(axis)


# If the x_axis is not empty, then create a chart 
if (x_axis.size != 0): 
    y_axis = axis.loc[(axis == 'Y') | (axis == 'y')]
    df.create_chart(output_data_wb, output_data_df, x_axis, y_axis, config_df)

#print(df.get_output_wb)
output_data_wb.save(df.get_output_wb + '.xlsx')