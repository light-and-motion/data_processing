import pandas as pd
from datetime import (datetime, timedelta, time, date)
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font
from openpyxl.chart import (ScatterChart, Reference, Series)
from openpyxl.chart.axis import DateAxis
import numpy as np
import xlsxwriter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# DOUBLE UNDERSCORE 
class Data_Processing: 
    CSV = '.csv'
    XLSX = '.xlsx'
    
    def __init__(self, choice, config_file, input_csv, output_name): 
        self.choice = choice
        self.config_file = config_file
        self.input_csv = input_csv 
        self.output_name = output_name
    
    
    def create_csv_dataframe(self, file, startLine): 
        """
        Takes in a CSV file of type lumensphere, multimeter, or serial
        and returns a DataFrame of the CSV file 

        Parameters: 
        file (String): Name of CSV file to be read 
        startLine (numpy.float64): Line numbers to skip at the start of file. If startLine is empty, 
        then no lines will be skipped. 

        Returns: 
        DataFrame: DataFrame of the CSV file 
        """
        if (pd.isnull(startLine)): 
            startLine = 0
        else: 
            startLine = startLine - 1 
        
        df = pd.read_csv(file + '.csv', skiprows= startLine, keep_default_na = True)

        return df

    def create_excel_dataframe(self, file, sheet): 
        """
        Returns a DataFrame of an Excel file 

        Parameters: 
        file (String): Name of Excel file to be read. 
        sheet (String): Name of sheet in Excel file to be read. 

        Returns: 
        DataFrame: DataFrame of the Excel file 
        """
        
        df = pd.read_excel(file + '.xlsx', sheet_name = sheet, dtype = {'Title': str})
        return df    

    def create_raw_Excelbook(self, data_df):  
        """
        Returns an Excel workbook to hold the data in a DataFrame

        Parameters: 
        data_df (DataFrame): DataFrame whose data will be read into the Excel workbook 

        Returns: 
        Workbook object: Excel workbook representation of DataFrame
        """
        
        wb = Workbook()
        ws = wb.active
        ws.title = 'Raw Data'

        for row in dataframe_to_rows(data_df, index = False, header = True):
            ws.append(row)
        wb.save(self.get_input_csv + '.xlsx')
        return wb

    
    def create_mapping_dataframe(self, raw_data_df, title_inputs, range_inputs, format):
        """
        Returns a DataFrame that contains only the columns in the CSV file that are being mapped 

        Parameters: 
        raw_data_df (DataFrame): DataFrame of CSV file 
        title_inputs (Series): Series that contains the columns we want mapped 
        range_inputs (Series): Series that contains the columns we want original data to be mapped to 

        Returns: 
        A Dataframe that contains only the columns in the CSV file that are being mapped
        """
        # initialize an empty df which will eventually store all mapped values 
        df = pd.DataFrame()
        
        # Find size of a column of df 
        max_size = raw_data_df.iloc[:,0].size
        

        # Determine the column with the largest range interval, whose index will be used for the entire DataFrame 'df'. 
        interval_index = self.largest_range_interval(range_inputs, max_size)
        range_list = self.find_range(range_inputs.loc[interval_index],max_size)
        start = range_list[0]
        end = range_list[1]
        df[title_inputs.loc[interval_index]] = raw_data_df[title_inputs.loc[interval_index]].iloc[start:end].reset_index(drop = True)
        if (not pd.isnull(format.iloc[interval_index]) and type(format.iloc[interval_index]) == int):
            df[title_inputs.loc[interval_index]] = self.round_numbers(df[title_inputs.loc[interval_index]], format.iloc[interval_index])

        # Drop rows/columns that have already been used above
        raw_data_df = raw_data_df.drop([title_inputs.loc[interval_index]], axis = 1)
        title_inputs = title_inputs.drop(labels = interval_index).reset_index(drop = True)
        range_inputs = range_inputs.drop(labels = interval_index).reset_index(drop = True)
        format = format.drop(labels = interval_index).reset_index(drop = True)

        # Store all the data to be mapped (range slicing included) into a df
        # Append each new series to 'df'
        for i in range(len(range_inputs)): 
            range_list = self.find_range(range_inputs.loc[i],max_size)
            start = range_list[0]
            end = range_list[1]
            new_series = raw_data_df[title_inputs.loc[i]].iloc[start:end].reset_index(drop = True)

            # Round numbers
            if (not pd.isnull(format.iloc[i]) and type(format.iloc[i]) == int):
                new_series = self.round_numbers(new_series, format.iloc[i])
            df[title_inputs.loc[i]] = new_series
        return df

    def round_numbers(self, series, round_to): 
        series = series.round(round_to)
        return series
    def largest_range_interval(self, range_inputs, max_size):
        """
        Returns the row index of the largest range interval in Excel  

        Parameters: 
        range_inputs (Series): Contains the range interval of all the columns to be mapped
        max_size (int): Size of 1 column in the DataFrame of the CSV file 

        Returns: 
        int: Returns the row index of the largest range interval in Excel 
        """ 
        max_interval = 0
        max_interval_index = 0
        i = 0
        #print(range_inputs)
        while (i < range_inputs.size): 
            range_list = self.find_range(range_inputs.iloc[i],max_size)
            range_difference = range_list[1]-range_list[0]
            if (range_difference > max_interval): 
                max_interval = range_difference
                max_interval_index = i
            i += 1
            
        return max_interval_index

     # Determine the starting and ending point of the data to be read 
    # Range is calculated against the row indexes of the Excel worksheet. Thus, the first
    # cell in a column will be located at row 2  
    
    def find_range(self, current_range, total_size): 

        """
        Returns a list of the starting and ending indices of the data you want to process for a Series. 

        Parameters: 
        current_range (float): The interval of the data to be read (inclusive) in start:end form
        total_size (int) - Size of the Series

        Returns: 
        List - A two element list whose first element is the starting row index and whose 
                second element is the ending row index. 
        """
        start = 0 
        end = total_size-1
        # interval is the entire column  
        if (pd.isnull(current_range)): 
            pass
        else: 
            range_list = current_range.split(':')
            if (range_list[0] == ''):
                end = int(range_list[1])-2
            elif (range_list[1] == ''): 
                start = int(range_list[0])-2
            else: 
                start = int(range_list[0])-2
                end = int(range_list[1])-2
                if (start < 0):
                    return [0, end] 
        return [start,end]
    

    def convert_to_time_object(self, series, unit):
        """
        Returns a series that contains a String representation of a time object in %H:%M:%S format 

        Parameters: 
        series (Series): The Series that is to be converted. Will either contain floats or a datetime object in form: %m/%d/%Y %H:%M:%S AM/PM
        unit (String): The time unit of the series. D = datetime object, H = hours, M = minutes, S = seconds 

        Returns: 
        Series object: String representation of time object in %H:%M:%S clocktime format
        """
        series = series.dropna()
        if (unit.upper() == 'D'): 
            for cur_datetime in series: 
                #print(cur_datetime)
                # Split the datetime object into a list by a space delimiter and store the %H:%M:%S  
                # portion into a variable 
                cur_datetime_list = cur_datetime.split()
                cur_time_list = cur_datetime_list[1].split('.')
                cur_time = cur_time_list[0]
                series.replace(cur_datetime, cur_time, inplace = True)

        else: #If the time series is in hours, minutes, or seconds 
            for time in series: 
                time_list = self.get_hours_minutes_seconds(time, unit)
                cur_time = str(time_list[0]) + ':' + str(time_list[1]) + ':' + str(time_list[2])
                series.replace(time, cur_time, inplace = True)
        return series

    def get_hours_minutes_seconds(self, time, time_unit):
        """
        Takes in an float representation of a a single unit of time, converts it to an integer, and 
        returns a list of the original time HH:MM:SS format. 

        Parameters: 
        time (float): Float time 
        time_unit: The unit of time that the parameter time is in

        Returns: 
        List: List holds three elements: the hour, minute, and second portion of the original time 
    
        """
        if (time_unit.upper() == 'H'): 
            time = time * 3600
        elif (time_unit.upper() == 'M'): 
            time = time * 60    
        time = int(time)
        hours = time // 3600 
        time = time % 3600
        minutes = time // 60 
        seconds = time % 60
        
        return [hours,minutes,seconds]

    def time_format(self, time_series, start_time): 
        """
        Takes in a String series in %H:%M:%S clocktime format and returns a time Series that gives the elapsed time in %H:%M:%S format. 

        Parameters: 
        time_series (Series): Series that contains String representations of clocktimes 

        Returns: 
        time_series (Series): Series that contains timedelta objects

        """

        time_series_modified = time_series.dropna()
    
        start_time = pd.to_timedelta(start_time)
        # Iterate through 'time_series_modified' which has the NA values dropped but replace the String with the timedelta in 
        # the original 'time_series.'
        for current_time in time_series_modified: 
            # Convert the String 'current_time' into a timedelta object and find the difference between 'current_time' and 'start_time'
            # to find the elapsed time. Convert the difference between the two times into a string and use the space 
            # delimiter to split it into a list. 
            difference= str(pd.to_timedelta(current_time)-start_time)
            difference_list = difference.split()
            # Store the time portion of the String into 'elapsed_time' and use the colon delimiter to split the time into a list 
            elapsed_time = difference_list[2]
            elapsed_time_list = elapsed_time.split(':')
            
            # Convert each element int the list into an integer and use the elements to produce a timedelta object 
            time = timedelta(hours = int(elapsed_time_list[0]), minutes = int(elapsed_time_list[1]), seconds = int(elapsed_time_list[2]))            
        
            #### convert to datetime object 
            #elapsedtime = datetime.strptime(elapsed_time, '%H:%M:%S').time()
            time_series.replace(current_time, time, inplace = True)
           
        return time_series

    
    def create_plotted_workbook(self): 
        """
        Returns an empty Excel workbook of the data to be plotted with the title of the
        default worksheet labeled as "Output Data."
        """
        
        wb = Workbook()
        ws = wb.active
        ws.title = 'Output Data'
        return wb

    def convert_columns(self, config_df, col_names):
        """
        Returns config_df where: 
            a) column letters in the 'input' column of 'config_df' have been replaced by column titles
            b) column letters in the 'output' column of 'config_df' have been replaced by column numbers
            c) 

        Parameters: 
        config_df (DataFrame): DataFrame that contains the 'mapped data portion' of the configuration file 
        col_names (Series): Series that contains the titles of the columns to be mapped 

        Returns: 
        DataFrame: Altered version of 'config_df' where elements of 'input' and 'output' columns have been altered  
        """
        
        self.letter2title(config_df['Input'], col_names)
        self.letter2int(config_df['Output'])
        config_df['Title'] = self.default_titles(config_df['Title'], config_df['Input'])

        return config_df
    
    # Converts the location format of the input columns from letters to new_titles  
    def letter2title(self, letter_series, names):
        """
        Converts the data inside a Series from Excel column letters to its column title 

        Parameters: 
        letter_series (Series object): Series that holds the Excel column letters

        names (Series object): Series that holds the column titles 

        Returns: 
        void 
        """
        indices = self.letter2int(letter_series)
        x = 0
        for col_letter in letter_series: 
            index = indices.loc[x]      
            title = names[index-1]
            letter_series.replace(col_letter, title, inplace=True)
            x += 1
    
    def letter2int(self, letter_series):
        """
        Takes in a series of letters and returns a series mapped to the 
        corresponding integer number

        Source: https://www.geeksforgeeks.org/find-excel-column-number-column-title/

        Parameters: 
        letter_series (Series object): Series that holds the Excel column letters

        Returns: 
        Series object: Series that holds the corresponding Excel column numbers
        """
        result = 0
        for col_letter in letter_series: 
            result = 0
            for x in col_letter: 
                x = x.upper()
                result *= 26
                result += ord(x) - ord('A') + 1   
            letter_series.replace(col_letter, result, inplace=True)
        return letter_series
    
    def default_titles(self, new_titles, input_titles): 
        x = 0
        for title in new_titles: 
            if (title == 'nan'): 
                new_titles.iat[x] = input_titles.iat[x]
            x += 1
        return new_titles

    def process_data(self, wb, df, config_df):
        """
        Maps the input data of the CSV file into the desired columns in the output Excel file 

        Parameters: 
        wb (Workbook object): Excel workbook that will store the results of the data processing 
        df (DataFrame): DataFrame that stores the data to be mapped 
        config_df (DataFrame): DataFrame that stores the data in the 'mapped data portion' of the configuration file  

        Returns: 
        Workbook object with data mapped to proper columns 
        """
        new_titles = config_df['Title']
        title_inputs = config_df['Input']
        outputs = config_df['Output']

        # Read in all the data 
        for j in range(new_titles.size): 
            self.read_in_values(wb, df, new_titles.iloc[j], title_inputs.iloc[j], outputs.iloc[j])
        return wb
    
    def read_in_values(self, wb, df, new_title, title_input, col_num):
        """
        Reads in the data of 1 input column into the Excel workbook 

        Parameters: 
        wb (Workbook object): 
        wb (Workbook object): Excel workbook that will store the results of the data processing 
        df (Series): DataFrame that stores the data to be mapped 
        new_title (String): New column title of the mapped data 
        title_inputs (String): Current column title of the series that is being mapped    
        col_num (int): Number of column the data is being mapped to   
        """ 
        ws = wb.active
        header = ws.cell(row=1, column = col_num) 
        header.value = new_title
        header.font = Font(bold=True)
        col_index = title_input
        
        # Indices: i retrieves the data in the column 
        #          cellRow ensures that the data is being mapped to the current cell in the Excel worksheet
        cellRow = 2 
        i = 0
        size = df[col_index].size
        while (i < size):   
            ws.cell(row = cellRow, column = col_num).value = df.loc[i,col_index]
            cellRow += 1
            i += 1
 
    def make_chart(self,axis):
        """
        Returns a list that indicates which columns will serve as the x-axis and y-axes of a plotted chart 

        Parameters: 
        axis (Series): Series that indicates which columns will serve as the x-axis and the y-axes

        Returns:
        List: A list, whose first element (should be) a one-element Series of the column that will serve as the x-axis 
                and whose second element is a Series of the column(s) that will serve as the y-axes
        """ 
        x_axis = axis.loc[(axis == 'x') | (axis == 'X')]
        y_axis = axis.loc[(axis == 'y') | (axis == 'Y')]
        return [x_axis, y_axis]

    def create_chart(self,wb, outputs_data_df, x_axis, y_axis, config_df_1, config_df_2): 
        """
        Creates a chart of the plotted data in a new worksheet of the output Excel workbook

        Parameters: 
        wb (Workbook object): Excel workbook of the mapped data 
        outputs_data_df (DataFrame) - DataFrame of the mapped data 
        x_axis (Series): Series that indicates which column will serve as the x-axis 
        y_axis (Series): Series that indicates which column(s) will serve as the y-axes
        config_df_1 (DataFrame): DataFrame that stores the data in the 'mapped data portion' of the configuration file  
        config_df_2 (DataFrame): DataFrame that stores the data in the 'general settings' of the configuration file 
        """
        #print(type(config_df_1))
        ws = wb.active
        
        title_inputs = config_df_1['Input']
        outputs = config_df_1['Output']
        new_titles = config_df_1['Title']
        graph_title = config_df_2['Graph Title']

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
        for row in y_axis_rows: 
            y = Reference(ws, min_col = outputs.loc[row], min_row = 2, max_row = row_size)
            s = Series(y,x,title=new_titles.loc[row])
            chart.append(s)
        
        chart.x_axis.title = new_titles.loc[x_axis_row]
        
        # situate x-axis below negative numbers 
        chart.x_axis.tickLblPos = "low"

        # Determine whether not there is more than 1 y-axis, which would necessitate the 
        # creation of a legend. 
        create_legend = self.chart_legend(y_axis_rows) 
        if (not create_legend): 
            chart.y_axis.title = new_titles.loc[y_axis_rows[0]]
            chart.legend = None 
        
        # Title the chart
        chart.title = self.chart_title(new_titles, graph_title, x_axis_row, y_axis_rows)

          # Determine whether grid lines should be on or off. By default it is on. 
        grid_lines = self.grid_lines(config_df_2['Grid Lines'].loc[0])
        if (not grid_lines): 
            
            chart.x_axis.majorGridlines = None 
            chart.y_axis.majorGridlines = None

        # Chart scaling 
        scale = self.chart_scaling(config_df_2['X Min'].loc[0], config_df_2['X Max'].loc[0], config_df_2['Y Min'].loc[0], 
                    config_df_2['Y Max'].loc[0])
        chart.x_axis.scaling.min = scale[0]
        chart.x_axis.scaling.max = scale[1]
        chart.y_axis.scaling.min = scale[2]
        chart.y_axis.scaling.max = scale[3]

        
        cs.add_chart(chart)


    def chart_legend(self, y_axis_rows):
        """
        Determines the need for a chart legend in the chart. If there is only 1 y-axis, then 
        title the y-axis instead and remove the legend. 

        Parameters: 
        y_axis_rows (Series): Series that indicates which columns will serve as the y-axes of the chart. 
        
        Returns: 
        bool: True if a chart legend is necessary. False if it is not. 
        """
        if (len(y_axis_rows) == 1): 
            return False
        return True
        
    ### Default chart title: If there is no given chart title then chart title will be: 
        #   'All y-axis vs x-axis'
    def chart_title(self, new_titles, graph_title, x_axis_row, y_axis_rows):
        """
        Returns the chart title. 

        Parameters: 
        new_titles (Series): Series that will be used to give a default chart title if no chart title is given 
        graph_title (Series): Series that will contain the given chart title
        x_axis_row (Series): Series that stores the index location of the column to serve as the x_axis
        y_axis_row (Series): Series that stores the index location(s) of the column(s) to serve as the y-axes 

        Returns: 
        String: Title of chart. If no title is given, then the chart title will default to '[All] y-axes vs x-axis'
        """
        # Note: A column with 'NaNs' is not considered empty. 
        if (graph_title.dropna().empty): 
            title = ''
            for i in range(y_axis_rows.size-1): 
                title += new_titles.loc[y_axis_rows[i]] + ", "
            title += new_titles.loc[y_axis_rows[y_axis_rows.size-1]] + " vs " + new_titles.loc[x_axis_row]
        else: 
            title = graph_title.loc[0]
        return title

    # Determines the need for a chart legend
    #   If there is only 1 y-axis, title the y_axis and delete the legend  

    def grid_lines(self, choice): 
        """
        Returns True if grid lines will be on chart, False otherwise

        Parameters: 
        choice (str): String will either be 'yes', 'no', or null (case insensitive) to indicate grid line settings

        Returns: 
        bool: True if chart will have grid lines, False if it will not 
        """
        if (pd.isnull(choice) or choice.upper() == 'YES'): 
            return True
        return False 

    def chart_scaling(self, x_min, x_max, y_min, y_max): 
        """
        Returns a list of the settings for the minimum and maximum of the x and y axis 

        Parameters: 
        x_min (*np.int64 or np.float64): Minimum value on x-axis scale 
        x_max (*np.int64 or np.float64): Maximum value on x-axis scale
        y_min (*np.int64 or np.float64): Minimum value on y-axis scale
        y_max (*np.int64 or np.float64): Maximum value on y-axis scale 

        *should be  

        Returns: 
        A list of the settings for the minimum and maximum of the x and y axis.
        """
        x_min_scale = None
        x_max_scale = None
        y_min_scale = None
        y_max_scale = None
        if (not pd.isnull(x_min) and (type(x_min) == np.float64 or type(x_min) == np.int64)): 
            x_min_scale = x_min
        if (not pd.isnull(x_max) and (type(x_min) == np.float64 or type(x_min) == np.int64)): 
            x_max_scale = x_max
        if (not pd.isnull(y_min) and (type(x_min) == np.float64 or type(x_min) == np.int64)): 
            y_min_scale = y_min
        if (not pd.isnull(y_max) and (type(x_min) == np.float64 or type(x_min) == np.int64)): 
            y_max_scale = y_max
        return [x_min_scale, x_max_scale, y_min_scale, y_max_scale]
        
    def make_jpeg(self, mapping_df, x_axis_list, y_axis_list, config_df_1, config_df_2, output_name):  
        """
        Produces a JPG file of the chart in matplotlib 

        Parameters: 
        mapping_df (DataFrame): DataFrame that contains only the columns in the CSV file that are being mapped 
        x_axis (Series): Series that indicates which column will serve as the x-axis 
        y_axis (Series): Series that indicates which column(s) will serve as the y-axes
        config_df_1 (DataFrame): DataFrame that stores the data in the 'mapped data portion' of the configuration file  
        config_df_2 (DataFrame): DataFrame that stores the data in the 'general settings' of the configuration file 
        output_name (String): Name JPG file will be saved as 
        """
        new_titles = config_df_1['Title']
        title_inputs = config_df_1['Input']
        graph_title = config_df_2['Graph Title']

        
        # plot multiple lines on a single graph
        # As matplotlib does not allow datetime.time objects to be set as an axis, must convert to a 
        # datetime object to plot on graph.  
        x_axis = mapping_df[title_inputs[x_axis_list.index[0]]].dropna()
        #print(x_axis.head())
        if (not config_df_2['Time Axis'].dropna().empty):
            #datetime_x_axis = pd.Series(self.convert_timedelta_to_datetime(x_axis))
            x_axis = pd.Series(self.convert_timedelta_to_datetime(x_axis))
      
        fig, ax = plt.subplots(1,1)
        for new_y_index in y_axis_list.index: 
            new_y_axis = title_inputs[new_y_index]
            plt.plot(x_axis, mapping_df[new_y_axis].dropna(), label = new_titles.iloc[new_y_index])
    
        
        # gives the rows that holds the titles of the columns to be plotted 
        x_axis_rows = x_axis_list.index[0] 
        y_axis_rows = y_axis_list.index 
        
        # set the labels and/or legend of the chart 
        plt.xlabel(new_titles[x_axis_list.index[0]])
        create_legend = self.chart_legend(y_axis_rows)
        if (create_legend):
            plt.legend(loc='upper left')
        else: 
            plt.ylabel(new_titles[y_axis_list.index[0]])

            # set the title 
        title = self.chart_title(new_titles, graph_title, x_axis_rows, y_axis_rows)
        plt.title(title)  
        
        # set gridlines 
        grid_lines = self.grid_lines(config_df_2['Grid Lines'].loc[0])
        if (grid_lines): 
            plt.grid(b = True)
        
        # date formatter 
        if (not config_df_2['Time Axis'].dropna().empty):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            fig.autofmt_xdate()

        # Chart scaling 
        scale = self.chart_scaling(config_df_2['X Min'].loc[0], config_df_2['X Max'].loc[0], config_df_2['Y Min'].loc[0], 
                    config_df_2['Y Max'].loc[0])
        plt.xlim(scale[0], scale[1])
        plt.ylim(scale[2], scale[3])

        # Chart scaling 
        scale = self.chart_scaling(config_df_2['X Min'].loc[0], config_df_2['X Max'].loc[0], config_df_2['Y Min'].loc[0], config_df_2['Y Max'].loc[0])
        plt.xlim(scale[0], scale[1])
        plt.ylim(scale[2], scale[3])

        # save the graph 
        plt.savefig(output_name + '.jpeg') 

    def convert_timedelta_to_datetime(self,timedelta_series): 
        """
        Takes in a Series that contains timedelta objects and returns a Series that contains datetime objects

        Parameters: 
        timedelta_series (Series): Series that contains timedelta objects

        Returns: 
        Series that contains datetime objects 
        """
        # convert 'timedelta_series' to type String 
        timedelta_str_series = timedelta_series.astype(str)
        #print('timedelta_str_series')

        # split 'timedelta_str_series' using the space delimiter and store the results into a list
        timedelta_str_list = [time.split() for time in timedelta_str_series]
        #print('timedelta_str_list')
        
        
        # Retrieve the 'time' portion of timedelta_str_list and store into another list  
        time_str_list = [time[2] for time in timedelta_str_list]
        #print('time_str_list')
        #print(time_str_list)
        # split 'time_str_list' using '.' delimiter and store results back into 'time_str_list'  
        time_str_list = [time.split('.') for time in time_str_list]

        # Retrieve the '%H:%M:%S' formatted time and store results back into list 
        time_str_list = [time[0] for time in time_str_list]

        # Convert 'time_str_list' into a series and turn each element into a datetime.time() object
        # Store in a new list. 
        time_str_series = pd.Series(time_str_list)
        time_obj = [datetime.strptime(time_str, '%H:%M:%S').time() for time_str in time_str_series]
        x_axis = [ datetime.combine(datetime.now(), time) for time in time_obj]
        #x_axis = pd.Series(x_axis)
        return x_axis
    
    @property
    def get_config_file(self): 
        return self.config_file
    @get_config_file.setter
    def set_config_file(self, config_file): 
        self.config_file = config_file

    @property
    def get_choice(self):
        return self.choice
    @get_choice.setter
    def set_choice(self, choice): 
        self.choice = choice

    @property
    def get_input_csv(self): 
        return self.input_csv
    @get_input_csv.setter
    def set_input_csv(self, input_csv): 
        self.input_csv = input_csv 
    
    ##### get_output_name returns an object, not a String
    @property
    def get_output_name(self): 
        return self.output_name 
    @get_output_name.setter
    def set_output_name(self, output_name): 
        self.output_name = output_name

    

