import user_interface
import pandas as pd
from data_processing import Data_Processing
from Dataframe import (DataFrame, ExcelDataFrame, MappedExcelDataFrame)
from CSV_DataFrame import CSVDataFrame
from File import (File, ChartFile, ExcelFile)
from JPEGFile import JPEGFile
from PDFFile import PDFFile

### Main execution block ###
user_interface.banner()

config_list = user_interface.choose_config()
config_sheet_list = config_list[0]
config_title = config_list[1]
input_csv = user_interface.choose_csv()
output_name = user_interface.choose_output_name()
df = pd.DataFrame()

# Read the two sheets of the configuration file: 'Mapped' and 'General' Settings into two different dataframes
mapped_df = MappedExcelDataFrame(config_title, df, config_sheet_list.sheetnames[0])
mapped_df.create_dataframe()
general_df = ExcelDataFrame(config_title, df, config_sheet_list.sheetnames[1])
general_df.create_dataframe()

# Create a dataframe to hold the raw CSV file and then read said dataframe into an Excel file 
raw_data_df = CSVDataFrame(input_csv, df, mapped_df, general_df)
raw_data_df.create_dataframe()

# Convert the 'Input' and 'Output' column letters into, respectively, column titles and numbers. 
# Keep a standalone copy of the 'Output.'
mapped_df.format(raw_data_df.get_column_labels)

# Store the columns we want mapped into a new dataframe 
output_df = raw_data_df.map_columns()

# Convert times into elapsed times 
raw_data_df.convert_to_elapsed_time(output_df)

# Output files 
excel_file = ExcelFile(mapped_df,general_df,output_df, output_name)
excel_file.output_excel()

jpeg_file = JPEGFile(mapped_df, general_df, output_df, output_name)
jpeg_file.output_JPEG()

pdf_file = PDFFile(mapped_df, general_df, output_df, output_name)
pdf_file.output()

#excel_output = df.make_file(config_df_2['Excel'].loc[0])
#jpeg_output = df.make_file(config_df_2['JPEG'].loc[0])
#pdf_output = df.make_file(config_df_2['PDF'].loc[0])
#txt_output = df.make_file(config_df_2['TXT'].loc[0])
# Grab the x-axis and y-axis and determine if a chart will be outputted 
''''
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
'''