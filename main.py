import user_interface
import pandas as pd
from data_processing import Data_Processing

### Main execution block ###
user_interface.banner()

# Asks user for type of data file to process based on numeric input. To be passed into choose_config. 
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


# Read the two sheets of the configuration file: 'Mapped' and 'General' Settings into two different dataframes
config_df_1 = df.create_excel_dataframe(config_title, config_file.sheetnames[0])
config_df_2 = df.create_excel_dataframe(config_title, config_file.sheetnames[1])


# Create a dataframe to hold the raw CSV file and then read said dataframe into an Excel file 
raw_data_df = df.create_csv_dataframe(input_csv, config_df_2)
raw_data_excel = df.create_raw_Excelbook(raw_data_df, data_choice)

# Convert the 'Input' and 'Output' column letters into, respectively, column titles and numbers. 
# Keep a standalone copy of the 'Output.'
col_names = raw_data_df.columns
output_columns = config_df_1['Output'].copy()
config_df_1 = df.convert_columns(config_df_1, col_names)

# Store the columns we want mapped into a new dataframe 
mapping_data_df = df.create_mapping_dataframe(raw_data_df, config_df_1['Input'], config_df_1['Title'], config_df_1['Range'], config_df_1['Format'])

# Formatting time columns to be in 'Elapsed Time'
time_unit = config_df_1['Time Unit'].dropna()

# Store the new time col in a new Series temporarily, 
# so the NaNs in mapping_data[time_title] won't convert
# the data type into object. 
if (not time_unit.empty): 
    index = time_unit.index.values
    time_indices = df.letter2int(config_df_1['Input Column Numbers'])
    for i in range(time_unit.size): 
        unit = time_unit.iloc[i]
        
        # Retrieve the column title of the 'time' column 
        time_index = time_indices.loc[index[i]]
        time_title = raw_data_df.columns[time_index-1]
        
        # Retrieve the start time and convert it to a str in elapsed time format 
        # start_time is a series of length 1 
        start_time = pd.Series(raw_data_df[time_title].loc[0])
        start_time = df.convert_to_time_object(start_time, unit)

        new_time_col = pd.DataFrame()
        # Index of the new column title is different than the index of the old column title 
        new_time_title = config_df_1['Title'].loc[time_unit.index[i]]
        new_time_col = df.convert_to_time_object(mapping_data_df[new_time_title], unit)
        df.time_format(new_time_col, start_time.loc[0])
        mapping_data_df[new_time_title] = new_time_col


# Output files 
excel_output = df.make_file(config_df_2['Excel'].loc[0])
jpeg_output = df.make_file(config_df_2['JPEG'].loc[0])
pdf_output = df.make_file(config_df_2['PDF'].loc[0])
txt_output = df.make_file(config_df_2['TXT'].loc[0])
# Grab the x-axis and y-axis and determine if a chart will be outputted 
axis = df.make_chart(config_df_1['Axis'])
create_chart = axis[0]
x_axis = None
y_axis = None
if (create_chart == True): 
    x_axis = axis[1]
    y_axis = axis[2]


output_data_wb = None

# Creating an Excel file 
if (excel_output):
    # Create workbook to hold plotted data
    output_data_wb = df.create_plotted_workbook()

    # Read the output data into an Excel file
    output_data_wb = df.process_data(output_data_wb, mapping_data_df, config_df_1, output_columns)

    # If the x_axis is not empty, then create a chart 
    if (create_chart): 
        df.create_chart(output_data_wb, mapping_data_df, x_axis, y_axis, config_df_1, config_df_2)
    output_data_wb.save(df.get_output_name + '.xlsx')

# Create the JPEG file and/or the chart portion of the PDF file 
if ((jpeg_output or pdf_output) and create_chart):
    df.make_jpeg(mapping_data_df, x_axis, y_axis, config_df_1, config_df_2, output_name, jpeg_output, pdf_output)

# Create the PDF file 
if (pdf_output): 
    df.make_pdf(output_name, mapping_data_df, create_chart)

# Create the text file 
if (txt_output): 
    df.make_txt(mapping_data_df, output_name, config_df_1['Format'])