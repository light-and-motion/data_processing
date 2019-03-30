import pandas as pd
from datetime import datetime
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

# Effectively determines whether or not a chart will be created. 
def make_chart(axis):

     # Extract the row index (if any) of the value that will serve as our x-axis 
    x_axis = axis.loc[(axis == 'x') | (axis == 'X')]
    return x_axis

def create_chart(wb, ws, title_inputs, outputs, outputs_data_df, x_axis, y_axis, new_titles, graph_title): 

    # Assume number of rows will be same throughout dataframe 
    row_size = outputs_data_df[title_inputs.loc[0]].size
     
    cs = wb.create_chartsheet()
    chart = ScatterChart()

    # Store the index location of the x-axis value 
    x_axis_row= x_axis.index[0] 

    # Store the column number where the x_axis is located 
    x = Reference(ws, min_col=outputs.loc[x_axis_row], min_row = 2, max_row = row_size)
    
    # Plot as many y-axes as indicated in the configuration file 
    
    y_axis_rows = y_axis.index
    #print(y_axis_rows)
    
    for row in y_axis_rows: 
        y = Reference(ws, min_col = outputs.loc[row], min_row = 2, max_row = row_size)
        s = Series(y,x,title=new_titles.loc[row])
        chart.append(s)
        
    
    chart.x_axis.title = new_titles.loc[x_axis_row]
    chart_legend(chart, y_axis_rows, new_titles)
    chart_title(chart, new_titles, graph_title, x_axis_row, y_axis_rows)

    cs.add_chart(chart)


# Determines the need for a chart legend
#   If there is only 1 y-axis, title the y_axis and delete the legend  
def chart_legend(chart, y_axis_rows, new_titles):
    if (len(y_axis_rows) == 1): 
        chart.y_axis.title = new_titles.loc[y_axis_rows[0]]
        chart.legend = None 
    return None 

### Default chart title: If there is no given chart title then chart title will be: 
    #   'All y-axis vs x-axis'
def chart_title(chart, new_titles, graph_title, x_axis_row, y_axis_rows): 
    # Note: A column with 'NaNs' is not considered empty. 
    if (graph_title.dropna().empty): 
        title = ' '
        for i in range(y_axis_rows.size-1): 
            title += new_titles.loc[y_axis_rows[i]] + ", "
        title += new_titles.loc[y_axis_rows[y_axis_rows.size-1]] + " vs " + new_titles.loc[x_axis_row]
        chart.title = title
    else: 
        chart.title = graph_title.loc[0]
    
def time_format(datetime_series): 
    start_datetime = datetime_series.loc[0]
    start_list = start_datetime.split()
    start_time = pd.to_timedelta(start_list[1])
    
    
    for cur_datetime in datetime_series: 

        # Split the datetime string into a list by a space delimiter 
        # and store the HH:MM:SS portion into a variable. 
        cur_datetime_list = cur_datetime.split() 

        # Store the time portion into cur_time and convert it to a timedelta object 
        cur_time = pd.to_timedelta(cur_datetime_list[1])

        # Find the difference between the current time and the start time. 
        # Convert the timedelta object into a string and split string into a list
        # by space delimiter.  
        difference= str(cur_time-start_time)
        difference_list = difference.split()

        # Store the time portion of the string into elapsed_time
        elapsed_time = difference_list[2]

        # Convert elapsed_time to a datetime object and store the result in the date column 
        elapsed_time = datetime.strptime(elapsed_time, "%H:%M:%S").time()
        datetime_series.replace(cur_datetime, elapsed_time, inplace = True)
    return datetime_series
        
        
        
    
############################# END FUNCTIONS #####################################################################
####################################################### MAIN ###############################################################################  
# Retrieve the raw data file and store the data in the dataframe. Skip line 0, as it contains the title. 
raw_data_df = pd.read_csv('Derived Data Imjin 800.csv',header = 1, keep_default_na = False)

#raw_data_df = pd.read_csv('Full Runtime 5600K Cree LED Production Stella EL.csv',header = 1, keep_default_na = False)
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

#Remember that loc/iloc can be used to access columns AND rows. In series, where there is only 1 column,
#loc will be used to access rows only. Rows are always accessed by row numbers (integers).


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

# EDIT: Used replace function to change values! 
for i in range(0, num_inputs.size): 
    num_inputs.replace(num_inputs.loc[i], letter2int(num_inputs.loc[i]), inplace = True)
    title_inputs.replace(title_inputs.loc[i],letter2title(title_inputs.loc[i], col_names), inplace = True)
    outputs.replace(outputs.loc[i], letter2int(outputs.loc[i]), inplace = True)
   

   

# output_data_df will hold all the columns that we want to plot later

# We will use col_titles_inputs as indices to extract from the raw data the columns that we want plotted
# Note: Even though only one column is being extracted at a time, the column being extracted 
# is stored in a dataframe as only dataframes, not series!, can combine with other dataframes. 

output_data_df = raw_data_df[[title_inputs.loc[0]]]


for i in range(1, num_inputs.size): 
    additional_df = raw_data_df[[title_inputs.loc[i]]]
    output_data_df = output_data_df.join(additional_df)

    

output_data_df['Date/Time'] = time_format(output_data_df['Date/Time']) 
print(output_data_df['Date/Time'].head())

# Create a new workbook to hold the plotted data 
output_data_wb = Workbook()
ws = output_data_wb.active
ws.title = 'Output Data'

# Read the output data into an Excel file
output_data_wb = process_data(output_data_wb, ws, output_data_df, col_titles, num_inputs, title_inputs, outputs)

##### Chart creation 

# Call make_chart() to determine if we need to create a chart 
x_axis = make_chart(axis)

# If the x_axis is not empty, then create a chart 
if (x_axis.size != 0): 
    y_axis = axis.loc[(axis == 'Y') | (axis == 'y')]
    create_chart(output_data_wb, ws, title_inputs, outputs, output_data_df, x_axis, y_axis, col_titles, graph_title)
output_data_wb.save('LumenData.xlsx')
#output_data_wb.save('LumenData_Stella.xlsx')


    
    
    
            