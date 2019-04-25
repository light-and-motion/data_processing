# Data Processing
The purpose of this project is to develop an automated processing program that will streamline data formatting of routinely conducted experiments. The software will take in a lumensphere, multimeter, or serial CSV file and output an Excel, JPEG, and/or PDF file of the processed results. The Excel file will hold a spreadsheet and chart of the processed results. The JPEG file will consist of a chart made in matplotlib. The PDF will hold the table and the matplotlib chart. 

## Running 
User will need a CSV file and a configuration file. The configuration file should be an Excel file and contain two worksheets. There are no restrictions on the names of the sheets. 

To run the program, run main.py.

## Background
There are several libraries that need to be imported for this program to run: numpy, pandas, openpyxl, matplotlib, pdfkit, PyPDF2, and os. 

'Sheet 1' of the configuration file gives the ‘Mapped Settings’ of the program. The columns should be titled: 
> **Input | Output | Format | Time Unit | Axis | Title | Range**

**_Except for 'Title' all inputs are case insensitive._**

Each row in the configuration file corresponds to a single column of data in the CSV file. 
- **Input**: Column letters of the columns we want mapped
- **Output**: Column letters of the columns we want the processed data to be mapped to in the output Excel file 
- **Format**: Sig figs we want the data to be rounded to
- **Time Unit**: How time is represented. 'D' is datetime, 'H' is hours, 'M' is minutes, and 'S' is seconds    
- **Axis**: Indicate whether CSV column will serve as an axis on the graph. 'X' for x-axis, 'Y' for y-axis. Can have multiple y-axis
- **Title**: Title of the CSV column in the output files 
- **Range**: Interval of the data in the CSV column to be processed 

'Sheet 2' gives the 'General Settings' of the program. The columns should be titled: 
> **Graph Title | Start Row | X Min | X Max | Y Min | Y Max | Grid Lines | Excel | JPEG | PDF** 

**_All inputs are case insensitive._**

Each column will contain only 1 value. 

- **ChartTitle**: Title of chart
- **Start Row**: Row to begin processing CSV file 
- **X Min**: Minimum value on x-axis of chart
- **X Max**: Maximum value on x-axis of chart
- **Y Min**: Minimum value on y-axis of chart
- **Y Max**: Maximum value on y-axis of chart 
- **Grid Lines**: Indicate whether grid lines on chart will be turned on or off
- **Excel**: Indicate whether an Excel file of processed results will be generated
- **JPEG**: Indicate whether a JPEG file of processed results will be generated
- **PDF**: Indicate whether a PDF file of processed results will be generated 


### Default Options

**_'--' indicates that there will be no error generation if no value is inputted._**

In 'Sheet 1': 
- **Input**: N/A
- **Output**: N/A
- **Format**: --
- **Time Unit**: --
- **Axis**: --
- **Title**: Title of the column in the CSV file 
- **Range**: All 

In 'Sheet 2': 
- **Graph Title**: Syntax will be '\[All] y-axes vs x-axis'
- **Start Row**: 1
- **X Min**: --
- **X Max**: --
- **Y Min**: --
- **Y Max**: --
- **Grid Lines**: Yes
- **Excel**: Yes
- **JPEG**: Yes
- **PDF**: Yes

## Restrictions: 
- Cannot set scale limits on elapsed times, as Excel and matplotlib cannot scale datetime or timedelta objects. 
- Cannot set float scale limits in matplotlib. 
- matplotlib scales break down when the minimum and maximum are too far apart, i.e. 20 and 1000
- Excel can graph axes with different lengths. Matplotlib cannot. 
- **Range** column must be formatted so it is read as 'Text,' otherwise it will be converted into time. 
- Milliseconds will be removed when converting into elapsed time. 
- A JPEG file will not be generated if a chart is not processed, even if **JPEG** is set to 'Yes.' An Excel and PDF file can still be generated without a chart addition. 

## Future Refinements
- Format PDF so the page containing the table and the chart are the same size. Center the table. 
- Allow users who have already had their CSV files read into an Excel file to skip processing their CSV again. 
- Replace text interface with a GUI. 
- Improve algorithm for adjusting column widths. 
- Look into creating a Time class.


