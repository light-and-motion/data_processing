import pandas as pd
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import (ScatterChart, Reference, Series)

############################# FUNCTIONS #####################################################################
# Converts a column letter to its corresponding integer.
# https://www.geeksforgeeks.org/find-excel-column-number-column-title/
def letter2int(letters):
    result = 0
    for x in letters: 
        x = x.upper()
        result *= 26
        result += ord(x) - ord('A') + 1
    return result 

# Converts the location format of the input columns from letters to new_titles  
def letter2title(letters, names):
    
    index = letter2int(letters)
    title = names[index-1]
    return title
    


# Store the data of the input columns of the CSV into the desired output columns in Excel 
# new_titles will be to create the new names of the columns
# num_inputs will be used to locate the cells where we want to store our data 
# title_inputs will be used to retrieve the column datas 
def process_data(wb, ws, df, new_titles, num_inputs, title_inputs, outputs):


    # Read in all the data 
    for j in range(new_titles.size): 
        # Append and bold the header of input column to the first row of its desired column location in Excel. 
        header = ws.cell(row=1, column = outputs.iloc[j]) 
        header.value = new_titles.iloc[j]
        header.font = Font(bold=True)
        col_index = title_inputs.iloc[j]
        for i in range(df[col_index].size): 

            ws.cell(row = i+2, column = outputs.loc[j]).value = df.loc[i,col_index]
    
    
    return wb
def create_chart(wb, ws, title_inputs, outputs, outputs_data_df, axis, new_titles, graph_title): 
    cs = output_data_wb.create_chartsheet()
    chart = ScatterChart()
    
    # Assume number of rows will be same throughout dataframe 
    row_size = outputs_data_df[title_inputs.loc[0]].size
    x_axis_row = 0
    y_axis_rows = []
    
    # Find the x-axis OPTIMIZE 
    i = 0
    x = Reference(ws, min_col=outputs.loc[0], min_row = 2, max_row = row_size)
    for x in axis: 
        if (not pd.isnull(x) and str(x).upper() == 'X'): 
            x = Reference(ws, min_col=outputs.loc[i], min_row = 2, max_row = row_size)
            x_axis_row = i
            break
        i += 1

    # Plot as many y-axes as indicated in the configuration file 
    i = 0
    for y in axis: 
        if (not pd.isnull(y) and str(y).upper() == 'Y'): 
            y = Reference(ws, min_col= outputs.loc[i], min_row=2, max_row= row_size)
            y_axis_rows.append(i)
            s = Series(y,x,title=new_titles.loc[i])
            chart.append(s)
        i += 1
    
    chart.x_axis.title = new_titles.loc[x_axis_row]

    ### Chart legend 
    # If there is only 1 y-axis, title the y_axis and delete the legend  
    if (len(y_axis_rows) == 1): 
        chart.y_axis.title = new_titles.loc[y_axis_rows[0]]
        chart.legend = None
        
    ### Default chart title: If there is no given chart title then chart title will be: 
    #   'all y-axis vs x-axis'
    
    if (pd.isnull(graph_title.loc[0])): 
        title = ' '
        for i in range(len(y_axis_rows)-1): 
            title += new_titles.loc[y_axis_rows[i]] + ", "
        title += new_titles.loc[y_axis_rows[len(y_axis_rows)-1]] + " vs " + new_titles.loc[x_axis_row]
        chart.title = title
    else: 
        chart.title = graph_title.loc[0]
    cs.add_chart(chart)

############################# END FUNCTIONS #####################################################################
####################################################### MAIN ###############################################################################  
# Retrieve the raw data file and store the data in the dataframe. Skip line 0, as it contains the title. 
raw_data_df = pd.read_csv('Derived Data Imjin 800.csv',header = 1, keep_default_na = False)

# Create a new Workbook and change the title of the active Worksheet 
raw_data_wb = Workbook()
ws = raw_data_wb.active
ws.title = 'Raw Data'

# Read the raw data into worksheet 1 and save the workbook
for row in dataframe_to_rows(raw_data_df, index = False, header = True):
    ws.append(row)
raw_data_wb.save("Lumensphere Raw Data.xlsx")
 
    
# Reuse raw data dataframe and store the contents of the Excel file (which was copied from the CSV file)
# Store the column names of the raw data (in Excel)

col_names = raw_data_df.columns





# QUESTION: Why is loc/iloc interchangeable sometimes and not interchangeable at other times. 
'''
Remember that loc/iloc can be used to access columns AND rows. In series, where there is only 1 column,
loc will be used to access rows only. Rows are always accessed by row numbers (integers).
'''

# 0pen the Lumensphere configuration file and store the contents of Input, Output, and Axis Title 
# into different series (not dataframe)! 

# num_inputs holds the locations of the columns that we want (in letter format). 
# (Letters will later be converted to its corresponding column number).
# title_inputs holds another copy of the letters of the columns that we want. 
# (Letters will later be converted to original column col_titles).
# outputs holds the locations of the columns that we want to read the original data into
# col_titles will hold the new names that we want to call our columns 

config_df = pd.read_excel('LumenConfig.xlsx', sheet_name = 'Sheet1')
num_inputs= config_df['Input']
title_inputs = config_df['Input'].copy()
outputs = config_df['Output']
col_titles = config_df['Title']
formats = config_df['Format']
axis = config_df['Axis']
graph_title = config_df['Graph Title']



# ########################## Could be converted into functions 
# Convert the letter elements of inputs into integers and Strings and outputs into integers 
# so we can later use them as indices in different ways. 
for i in range(0, num_inputs.size): 
    num_inputs.loc[i] = letter2int(num_inputs.loc[i])
    title_inputs.loc[i] = letter2title(title_inputs.loc[i], col_names)
    outputs.loc[i] = letter2int(outputs.loc[i])
    
    

# output_data_df will hold all the columns that we want to plot later

# We will use col_titles_inputs as indices to extract from the raw data the columns that we want plotted
# Note: Even though only one column is being extracted at a time, the column being extracted 
# is stored in a dataframe as only dataframes, not series!, can combine with other dataframes. 

output_data_df = raw_data_df[[title_inputs.loc[0]]]


for i in range(1, num_inputs.size): 
    additional_df = raw_data_df[[title_inputs.loc[i]]]
    output_data_df = output_data_df.join(additional_df)

    

output_data_df['Date/Time'] = pd.to_datetime(output_data_df['Date/Time'])
output_data_df['Date/Time'] = (output_data_df['Date/Time']- output_data_df['Date/Time'].iloc[0]).astype("timedelta64[s]")


# Create a new workbook to hold the plotted data 
output_data_wb = Workbook()
ws = output_data_wb.active
ws.title = 'Output Data'

# Read the output data into an Excel file
output_data_wb = process_data(output_data_wb, ws, output_data_df, col_titles, num_inputs, title_inputs, outputs)

# Create the chart 
create_chart(output_data_wb, ws, title_inputs, outputs, output_data_df, axis, col_titles, graph_title)
output_data_wb.save('LumenData.xlsx')



    
    
    
            