import user_interface
from data_processing import Data_Processing

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
output_wb = user_interface.choose_output_wb()

df = Data_Processing(data_choice, config_file, input_csv, output_wb)


# Retrieve the csv file and store its contents into a dataframe 
raw_data_df = df.create_csv_dataframe(input_csv)

# Read the raw dataframe into an Excel file 
raw_data_excel = df.create_raw_Excelbook(raw_data_df)


# Get the names of the columns and read the configuration file into config_df_1
# Then conver the column inputs and outputs into integers and titles to later use as indices 
col_names = raw_data_df.columns
config_df_1 = df.create_excel_dataframe(config_title, config_file.sheetnames[0])


config_df_2 = df.create_excel_dataframe(config_title, config_file.sheetnames[1])
config_df_1 = df.convert_columns(config_df_1, col_names)
#print(config_df_1)

# mapping_data_df will hold all the columns that we want to plot later

# We will use col_titles_inputs as indices to extract from the raw data the columns that we want plotted
# Note: Even though only one column is being extracted at a time, the column being extracted 
# is stored in a dataframe as only dataframes, not series!, can combine with other dataframes. 

mapping_data_df = df.create_mapping_dataframe(raw_data_df, config_df_1['Input Column Title'])


# format time 
mapping_data_df['Date/Time'] = df.time_format(mapping_data_df['Date/Time']) 



# create workbook to hold plotted data
output_data_wb = df.create_plotted_workbook()


# Read the output data into an Excel file
output_data_wb = df.process_data(output_data_wb, mapping_data_df, config_df_1)


##### Chart creation 

# Call make_chart() to determine if we need to create a chart 
axis = config_df_1['Axis']
x_axis = df.make_chart(axis)


# If the x_axis is not empty, then create a chart 
if (x_axis.size != 0): 
    y_axis = axis.loc[(axis == 'Y') | (axis == 'y')]
    df.create_chart(output_data_wb, mapping_data_df, x_axis, y_axis, config_df_1, config_df_2)

#print(df.get_output_wb)
output_data_wb.save(df.get_output_wb + '.xlsx')
