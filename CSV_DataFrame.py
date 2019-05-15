from DataFrames import DataFrame
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime, timedelta

class CSVDataFrame(DataFrame): 
    """
    A class used to read a CSV file into a pd.df 

    Attributes: 
    general_settings (pd.df): Contains the settings that will be used to configure csv df  
    """
    def __init__(self,file_name, df, mapped_settings, general_settings): 
        super().__init__(file_name, df)
        self.mapped_settings = mapped_settings
        self.general_settings = general_settings

    def get_start_row(self):  
        start_ser = self.general_settings.get_column('Start Row')
        if (not start_ser.dropna().empty): 
            return start_ser.loc[0]-1
        return 0

    def get_stop_row(self): 
        stop_ser =  self.general_settings.get_column('Stop Row')
        if (not stop_ser.dropna().empty): 
            return stop_ser.loc[0] - self.get_start_row() - 1 
        return None

    def get_skip_first_row(self): 
        skip_ser = self.general_settings.get_column('Skip First Row')
        if (not skip_ser.dropna().empty and skip_ser.loc[0].upper() == 'YES'):
            return True
        return False
    
    def get_transpose(self): 
        transpose_ser = self.general_settings.get_column('Transpose')
        if (not transpose_ser.dropna().empty): 
            return transpose_ser.loc[0]
        return 'NO'


    def create(self): 
        """Returns a dataframe of the CSV file 

        Parameters: 
        file (str): Name of CSV file to be processed
        general_settings_2 (dataframe): 'General Settings' of the configuration file 
        """

        # Default values         
        startLine = self.get_start_row()
        stopLine = self.get_stop_row()
        skipLine = self.get_skip_first_row()
        transpose = self.get_transpose()

        # Read the CSV into the dataframe     
        self.df = self.df.append(self._read_csv_type(startLine, stopLine, transpose)) 
    
        if (transpose.upper() == 'YES'): 
            #TODO: Ask if N/A marker is to be kept or if the cells that contain it be empty instead. 
            stopLine 
            self.df = self._transpose(startLine, skipLine)
        
        if (skipLine): 
           self.df.drop(1, inplace=True)
          #  self.df.reset_index(drop = True)

        # Get rid of columns with all whitespace 
        self.df = self.df.dropna('columns', how='all')

        # Reset index to start at 0 after dropping column(s)
        self.df = self.df.reset_index(drop=True)
        
        # Search for the columns that have a PM time. (Note: Excel convert str times with a PM time into 24 hour time). 
        # For example, 1:27 PM is converted into 13:27.  
        datetime_str_columns = self._search_for_pm_times()

           
        # Format the PM time columns into 12 hour time format. 
        [self._date_parser(self.df[column_name]) for column_name in datetime_str_columns]        
        
        
        # Iterates through all the columns of the dataframe and converts the numeric values back into their proper datatype

        # Used in particular for: 
        #   a) transposed df: As the transpose() function converts the dtypes of the transposed dataframe all into 
        #                     objects when the original dtypes were mixed, the while loop converts the 
        #                     numeric values back into their proper dtype. 
        #   b) Columns with empty Strings: The empty String values conver the entire column into an object dtype. By dropping the empty strings, 
        #                     the column can be converted to numeric type.
        for column in self.df: 
            self.df[column].replace('', np.nan, inplace=True)
            self.df[column] = self.df[column].dropna()
            self.df[column] = pd.to_numeric(self.df[column], errors = 'ignore')

    def read_into_excel(self, input_name):  
        """Returns an Excel workbook that holds the CSV file in a dataframe
        Parameters: 
        data_df (dataframe): CSV file to be be read into the Excel workbook 
        choice (int): The type of file that is being read into Excel 
        """

        wb = Workbook()
        ws = wb.active
        ws.title = 'Raw Data'

        for row in dataframe_to_rows(self.df, index = False, header = True):            
            ws.append(row)
        
        wb.save(input_name + '.xlsx')

    def _read_csv_type(self, startLine, stopLine, transpose):
        """Returns the prototype dataframe of the CSV file 
        
        Parameters: 
        file (str):  Name of CSV file to be processed
        startLine (int): Row to begin processing CSV file
        stopLine (int): Row to stop processing CSV file
        transpose (str): Determines whether df is to be transposed 
        """ 

        # Read to the very end of the file  
        if (stopLine == None and transpose == 'NO'): 
            return pd.read_csv(self.file_name+ '.csv', 
                            skiprows= startLine, 
                            keep_default_na = False, 
                            encoding = 'ISO-8859-1')

        # Stop reading before the end of a file 
        elif (transpose.upper() == 'NO'):
            return pd.read_csv(self.file_name + '.csv', 
                            skiprows= startLine, 
                            nrows = stopLine, 
                            keep_default_na = False, 
                            encoding = 'ISO-8859-1')

        # Read to the very end and transpose df 
        elif (stopLine == None and transpose.upper() == 'YES'): 
            return pd.read_csv(self.file_name + '.csv', 
                            header = None, 
                            index_col= None, 
                            skiprows= startLine, 
                            keep_default_na = False, 
                            encoding = 'ISO-8859-1') 
        # Stop reading before the end and transpose df 
        # TODO: Elaborate further. (Add +1 to stopLine b/c data technically starts on second line?)
        else: 
            return pd.read_csv(self.file_name + '.csv', 
                            header = None, 
                            index_col= None, 
                            skiprows= startLine,
                            nrows = stopLine + 1,  
                            keep_default_na = False, 
                            encoding = 'ISO-8859-1') 

    
    def _transpose(self, startLine, skipLine): 
            """
            Returns a transposed df 

            Parameters: 
            df (df): df that is to be transposed
            startLine (int): Row to begin processing CSV file
            """
            # Logic to set the actual columns and indices in the transposed data
            self.df = self.df.transpose()
            self.df.rename(self.df.iloc[0], axis = 'columns', inplace = True)
            self.df.drop(0, inplace = True)
            
            #TODO: Research how dataframes are passed into functions. (pass by value or reference)
                    
            # As the transpose() function converts the dtypes of the transposed dataframe all into objects when the original dtypes 
            # were mixed, the while loop converts the numeric values back into their proper dtype
            
            return self.df
       
    def _search_for_pm_times(self):
        """ Returns a list that stores all the titles of the columns that contain PM times"""

        # Search the first row of every column in the dataframe, convert every value to strptime(%-m/%-d/%Y %H:%M:%S) or 
        # strptime(%-m/%d/%Y %H:%M). If a ValueError is NOT returned, then add the title of the column to the list. 
        datetime_str_column = []
        
        for column in self.df: 
            series = self.df[column]
            try: 
                for format in ('%m/%d/%Y %H:%M', '%m/%d/%Y %H:%M:%S'): 
                    datetime_str = str(series.loc[0])
                    datetime.strptime(datetime_str, format)
                    datetime_str_column.append(column)
            except ValueError: 
                pass 
        return datetime_str_column
        
    
    def _date_parser(self, datetime_str_series):
        """ Returns a series with its PM times formatted to look like AM times 
        
        Parameters: 
        datetime_str_series (series): Contains PM times that needs to be reformatted  
        """

        # Filter out AM time; they do not need to undergo re-formatting 
        datetime_str_pm = datetime_str_series[~datetime_str_series.str.contains('AM')]
        # Return a date format equal to the AM times 
        for datetime_str in datetime_str_pm:  
            datetime_str_list = datetime_str.split()
            date = datetime_str_list[0]
            time = datetime_str_list[1]
            time_list = time.split(':')
            hours = str(int(time_list[0])-12)
            minutes = time_list[1]
            if (len(time_list) == 3): 
                seconds = time_list[2]
            else: 
                seconds = '00'
            new_str = date + ' ' + hours + ':' +  minutes + ':' +  seconds + ' PM'   
            datetime_str_series.replace(datetime_str, new_str, inplace=True)
        return datetime_str_pm


    def map_columns(self): 
        """Returns a dataframe that contains only the CSV columns that are being processed 

        Parameters: 
        raw_data_df (dataframe): dataframe of CSV file 
        title_inputs (series): Original titles of the processed CSV columns 
        range_inputs (series): Interval of data we want read in each processed CSV column
        """
        title_inputs =  self.mapped_settings.get_column('Input')
        new_titles = self.mapped_settings.get_column('Title')
        range_inputs = self.mapped_settings.get_column('Range')
        format = self.mapped_settings.get_column('Format')
        raw_data = self.df.copy()
    
        # Initialize an empty dataframe which will eventually store all mapped values 
        mapped_df = pd.DataFrame()
        
        # Find size of dataframe column  
        max_size = raw_data.iloc[:,0].size
        
        # Determine the column with the largest range interval, whose index will be used for the entire dataframe. 
        interval_index = self._largest_range_interval(range_inputs, max_size)
        range_list = self._find_range(range_inputs.loc[interval_index],max_size)
        start = range_list[0]
        end = range_list[1]
        mapped_df[title_inputs.loc[interval_index]] = raw_data[title_inputs.loc[interval_index]].iloc[start:end].reset_index(drop = True)
        if (not pd.isnull(format.iloc[interval_index]) and type(format.iloc[interval_index]) == np.float64):
            mapped_df[title_inputs.loc[interval_index]] = self._round_numbers(raw_data[title_inputs.loc[interval_index]], int(format.iloc[interval_index]))
        mapped_df.rename({title_inputs.loc[interval_index]: new_titles.iloc[interval_index]}, axis = 'columns', inplace=True)

        # Drop the rows/columns that have already been used above
        raw_data = raw_data.drop([title_inputs.loc[interval_index]], axis = 1)
        title_inputs = title_inputs.drop(labels = interval_index).reset_index(drop = True)
        range_inputs = range_inputs.drop(labels = interval_index).reset_index(drop = True)
        format = format.drop(labels = interval_index).reset_index(drop = True)
        new_titles = new_titles.drop(labels = interval_index).reset_index(drop = True)

        # Store all the data to be processed into a dataframe and append each new column to the dataframe 
        for i in range(len(range_inputs)): 
            range_list = self._find_range(range_inputs.loc[i],max_size)
            start = range_list[0]
            end = range_list[1]
            new_series = raw_data[title_inputs.loc[i]].iloc[start:end].reset_index(drop = True)
            
            # Round numbers
            if (not pd.isnull(format.iloc[i]) and type(format.iloc[i]) == np.float64):
                new_series = self._round_numbers(new_series, int(format.iloc[i]))
            mapped_df[title_inputs.loc[i]] = new_series
            
            # Rename column titles
            mapped_df.rename({title_inputs.loc[i]: new_titles.loc[i]}, axis = 'columns', inplace=True)

        return mapped_df
    
    def _round_numbers(self, series, round_to): 
        """ Round numbers in 'series' to the number of decimal places indiciated by 'round_to'"""
        series = series.round(round_to)
        return series
    
    def _largest_range_interval(self, range_inputs, max_size):
        """ Returns the row index of the largest range interval  

        Parameters: 
        range_inputs (series): Interval of data we want read in each processed CSV column
        max_size (int) - Size of the CSV column 
        """ 
        
        max_interval = 0
        max_interval_index = 0
        i = 0
        while (i < range_inputs.size): 
            range_list = self._find_range(range_inputs.iloc[i],max_size)
            range_difference = range_list[1]-range_list[0]
            if (range_difference > max_interval): 
                max_interval = range_difference
                max_interval_index = i
            i += 1
            
        return max_interval_index
    
    def _find_range(self, current_range, max_size): 
        """Returns a list of the interval of data we want processed in a CSV column.

        The first elment in the list is the starting row index, the second element is the ending row index. 

        Parameters: 
        current_range (float): The interval of the data to be read in 'start:end' format (inclusive)
        max_size (int) - Size of the CSV column 
        """
        
        start = 0 
        end = max_size
        # Range is calculated against the row indexes of the Excel worksheet. Thus, the first
        # cell in a column will be located in row 2.   
        if (pd.isnull(current_range)): 
            pass
        else: 
            range_list = current_range.split(':')
            # Start at the very beginning and stop at a certain point 
            if (range_list[0] == ''):
                end = int(range_list[1])
            
            # Start at a certain point and go to the very end 
            elif (range_list[1] == ''): 
                start = int(range_list[0]) - 1 #- self.get_startRow()
            
            # Start and stop at certain points
            else: 
                start = int(range_list[0]) - 1 #- self.get_startRow()
                end = int(range_list[1])
            # Final check to make sure intervals are not out of bounds 
            #if (self.get_start_row() - start < 0):
             #   start = 0 
            if (end - 2 > max_size):
                    end = max_size
        #print(start, end)
        return [start,end]
    
    def convert_to_elapsed_time(self, output_df):
        """ Returns output_df with the time values converted into elapsed times
        
        Parameters: 
        output_df(df): df that contains the values to be converted 
        """ 

        # Grab the time units of the columns whose values is to be converted into elapsed times 
        time_units_df = self.mapped_settings.get_column('Time Unit').dropna()

        # If there are time values that need to be reformatted...
        if (not time_units_df.empty): 
            
            # 'index' contains the indices of the time columns in mapped_settings ('Sheet 1' of the configuration file) 
            all_time_indices = time_units_df.index.values
            #all_time_titles = self.mapped_settings.letter2int(self.mapped_settings.get_column('Input Column Numbers'))
            all_time_titles = self.mapped_settings.get_column('Input Column Numbers')
            
            # Iterate through all the time columns 
            for i in range(time_units_df.size): 
                
                # Grab the time unit of the column  
                unit = time_units_df.iloc[i]
                
                # Retrieve the original column title of the 'time' column. This is needed to find the starting time, especially
                # when the range of the mapped data set has been limited.  
                time_index = all_time_titles.loc[all_time_indices[i]]
                time_title = super().get_column_labels[time_index-1]
                
                # Retrieve the start time and convert it to a series of length 1 and type str in elapsed time format.  
                start_time = self._convert_to_elapsed_time_str_series(pd.Series(super().get_column(time_title).loc[0]), unit)

                # Create an empty df
                new_time_col = pd.DataFrame()
                
                # Retrieve the new title of the time column so you can retrieve its data set in output_df 
                new_time_title = self.mapped_settings.get_column('Title').loc[time_units_df.index[i]]
            
                # Convert the values in the column into elapsed times 
                new_time_col = self._convert_to_elapsed_time_str_series(output_df[new_time_title], unit)
                self._convert_to_timedelta(new_time_col, start_time.loc[0])
                output_df[new_time_title] = new_time_col

        return output_df

    def _convert_to_elapsed_time_str_series(self, series, unit):
        """Returns a series that contains a str representation of a time object in %H:%M:%S format 

        Parameters: 
        series (Series): The CSV column that is to be converted. Will either contain floats 
                            or a datetime object in %m/%d/%Y %H:%M:%S AM/PM format. 
        unit (str): The unit of time of the CSV column. D = datetime, H = hours, M = minutes, S = seconds 
        """

        series = series.dropna()

        # Creating a copy of 'series' to be iterated over. That way even if two cells have the same datetime, 
        # and both cells are replaced in the original 'series,' the for loop will not break when we iterate over the second copy.  
        series_copy = series.copy()

        # If the time series is a datetime object....
        if (unit.upper() == 'D'): 
            for cur_datetime in series_copy: 
                
                # Split the datetime object into a list by a space delimiter and store the %H:%M:%S  
                # portion into a variable 
                cur_datetime_list = cur_datetime.split()
                cur_time_list = cur_datetime_list[1].split('.')
                cur_time = cur_time_list[0]
                series.replace(cur_datetime, cur_time, inplace = True)
            
        #If the time series is in hours, minutes, or seconds...
        else:
            for time in series_copy: 
                time_list = self._get_hours_minutes_seconds(time, unit)
                cur_time = str(time_list[0]) + ':' + str(time_list[1]) + ':' + str(time_list[2])
                series.replace(time, cur_time, inplace = True)
        return series
    
    def _get_hours_minutes_seconds(self, time, time_unit):
        """Returns a list that holds the hours, minutes, and seconds of the given time. 

        Takes in a float representation of a a single unit of time, converts it into an integer, and 
        returns a list of the original time in %H:%M:%S format. 

        Parameters: 
        time (float): Given time to be converted
        time_unit: The unit of time that the given time is in
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

    def _convert_to_timedelta(self, time_series, start_time): 
        """Returns a series that contains timedelta objects. 

        Takes in a str series in %H:%M:%S format and returns a time series that gives the elapsed time in the same format. 

        Parameters: 
        time_series (series): str representation of time in %H:%M:%S
        """

        time_series_modified = time_series.dropna()
        start_time = pd.to_timedelta(start_time)

        # Iterate through 'time_series_modified' which has the NaN values dropped but replace the str with the timedelta in 
        # the original 'time_series.'
        for current_time in time_series_modified: 
            
            # Convert the str 'current_time' into a timedelta object and find the difference between 'current_time' and 'start_time'
            # to find the elapsed time. Convert the difference between the two times into a str and use the space 
            # delimiter to split it into a list. 
            difference= str(pd.to_timedelta(current_time)-start_time)
            difference_list = difference.split()
            
            # Store the time portion of the str into 'elapsed_time' and use the colon delimiter to split the time into a list 
            elapsed_time = difference_list[2]
            elapsed_time_list = elapsed_time.split(':')
            
            # Convert each element in the list into an integer and use the elements to produce a timedelta object 
            time = timedelta(hours = int(elapsed_time_list[0]), minutes = int(elapsed_time_list[1]), seconds = int(elapsed_time_list[2]))            
            
            # Replace 'current_time' with 'time' in 'time_series'
            time_series.replace(current_time, time, inplace = True)
    

    
            

   