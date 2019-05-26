from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from .dataframes import MyDataFrame, ExcelDataFrame, MappedExcelDataFrame



class CSVDataFrame(MyDataFrame): 
    """
    Extends MyDataFrame to read a CSV into a pandas dataframe. 

    Attributes
    ----------
    file_name : str
        Name of file to be read into CSV 
    df : pd.DataFrame
        Stores the data contained in the file 
    mapped_settings : MappedExcelDataFrame
        Contains the mapped settings in the configuration file
    general_settings : ExcelDataFrame
        Contains the general settings of the configuration file  
    """

    def __init__(self,file_name, df, mapped_settings, general_settings): 
        super().__init__(file_name, df)
        self.mapped_settings = mapped_settings
        self.general_settings = general_settings

    def get_start_row(self) -> int:  
        """Returns the first line number to be read from the CSV."""

        start_ser = self.general_settings.get_column('Start Row')
        if (not start_ser.dropna().empty):
            # Minus 1 because pandas is zero-indexed  
            return start_ser.loc[0]-1
        return 0

    def get_stop_row(self) -> int or None: 
        """Returns the last line number to be read from the CSV."""

        stop_ser =  self.general_settings.get_column('Stop Row')
        if (not stop_ser.dropna().empty): 
            return stop_ser.loc[0] - self.get_start_row() - 1 
        return None

    def is_first_row_skipped(self) -> bool : 
        """Returns True if there is a line number you want to skip that is between the first and 
        last line numbers."""

        skip_ser = self.general_settings.get_column('Skip First Row')
        if (not skip_ser.dropna().empty and skip_ser.loc[0].upper() == 'YES'):
            return True
        return False
    
    def is_df_transpose(self) -> str: 
        """Returns "YES" if dataframe is to be transposed, "NO" otherwise."""
        
        transpose_ser = self.general_settings.get_column('Transpose')
        if (not transpose_ser.dropna().empty and transpose_ser.loc[0].upper() == 'YES'): 
            return 'YES'
        return 'NO'


    def create(self): 
        """Returns a dataframe of the CSV."""

        # Default values         
        startLine = self.get_start_row()
        stopLine = self.get_stop_row()
        skipLine = self.is_first_row_skipped()
        transpose = self.is_df_transpose()

        # Read the CSV into the dataframe     
        self.df = self.df.append(self._read_csv_type(startLine, stopLine, transpose)) 
    
        if (transpose.upper() == 'YES'): 
            #TODO: Ask if N/A marker is to be kept or if the cells that contain it be empty instead. 
            stopLine 
            self.df = self._transpose(startLine, skipLine)
        
        if (skipLine): 
           self.df.drop(1, inplace=True)

        # Get rid of columns with all whitespace 
        self.df = self.df.dropna('columns', how='all')

        # Reset index to start at 0 after dropping column(s)
        self.df = self.df.reset_index(drop=True)
        
        # Search for the columns that have a PM time. (Note: Excel convert str times with a PM time into 
        # military time. For example, 1:27 PM is converted into 13:27. 
        datetime_str_columns = self._search_for_military_times()
           
        # Format the PM time columns into 12 hour clock format
        [self._date_parser(self.df[column_name]) for column_name in datetime_str_columns]        
        
        # Iterates through all the columns in the dataframe and converts the digit object values into their proper datatype

        # Used in particular for: 
        #   a) transposed df: As the transpose() function converts the dtypes of the transposed dataframe all into 
        #                     objects when the original dtypes were mixed, the while loop converts the 
        #                     digit values into numeric dtype. 
        #   b) Columns with empty Strings: The empty String values convert the entire column into an object dtype. 
        #                     By dropping the empty strings, the column can be converted int numeric dtype.
        for column in self.df: 
            self.df[column].replace('', np.nan, inplace=True)
            self.df[column] = self.df[column].dropna()
            self.df[column] = pd.to_numeric(self.df[column], errors = 'ignore')

    def read_into_excel(self, input_name):  
        """
        Reads a CSV into an Excel workbook. 

        Parameters
        ----------
        input_name : str
            Name of CSV 

        Returns
        ------- 
        openpyxl.Workbook
            Holds the CSV in an Excel file 
        """

        wb = Workbook()
        ws = wb.active
        ws.title = 'Raw Data'

        for row in dataframe_to_rows(self.df, index = False, header = True):            
            ws.append(row)
        
        wb.save(input_name + '.xlsx')

    def _read_csv_type(self, startLine, stopLine, transpose):
        """Reads the CSV into a prototype dataframe. 
        Returns the prototype dataframe of the CSV. 
        
        Parameters
        ----------
        startLine : int
            First line number read from CSV 
        stopLine : int
            Last line number read from CSV
        transpose : str
            Determines whether df is to be transposed 

        Returns
        ------- 
        pd.DataFrame
            Prototype dataframe of the CSV 
        """ 

        # Read to the very end of the file and do not transpose CSV 
        if (stopLine == None and transpose == 'NO'): 
            return pd.read_csv(self.file_name+ '.csv', 
                            skiprows= startLine, 
                            keep_default_na = False, 
                            encoding = 'ISO-8859-1')

        # Read to a specific line number and do not transpose CSV 
        elif (transpose.upper() == 'NO'):
            return pd.read_csv(self.file_name + '.csv', 
                            skiprows= startLine, 
                            nrows = stopLine, 
                            keep_default_na = False, 
                            encoding = 'ISO-8859-1')

        # Read to the very end and transpose CSV 
        elif (stopLine == None and transpose.upper() == 'YES'): 
            return pd.read_csv(self.file_name + '.csv', 
                            header = None, 
                            index_col= None, 
                            skiprows= startLine, 
                            keep_default_na = False, 
                            encoding = 'ISO-8859-1') 
        # Read to a specific line number and transpose CSV 
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
            Transpose the dataframe.  

            Parameters
            -----------
            startLine : int
                First line number read from CSV 
            skipLine : bool
                True if second line number (relative to startLine) is skipped

            Returns
            ------- 
            pd.DataFrame
                Transposed dataframe
            """
            # Logic to set the actual columns and indices in the transposed dataframe 
            self.df = self.df.transpose()
            self.df.rename(self.df.iloc[0], axis = 'columns', inplace = True)
            self.df.drop(0, inplace = True)
            
            #TODO: Research how dataframes are passed into functions. (pass by value or reference)
            
            return self.df
       
    def _search_for_military_times(self): 
        """
        Goes through the self.df and searches for series whose values are 
        str representations of miltiary datetimes 

        Parameters 
        ----------
        None 
        
        Returns
        -------
        list
            Contains the column labels of the columns with str representations of military datetimes
        """

        datetime_str_column = []
        i = 0
        for column in self.df: 
            series = self.df[column]
            for format in ('%m/%d/%Y %H:%M', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S.%f'): 
                datetime_str = str(series.loc[0])
                try: 
                    datetime.strptime(datetime_str, format)
                    datetime_str_column.append(column)
                except ValueError: 
                    continue
                i += 1
    
        return datetime_str_column
        
    
    def _date_parser(self, datetime_str_series) -> pd.Series:
        """
        Converts a series that holds string representations of military datetime into 
        a series that holds string representations of standard datetime.   
         
        Parameters
        ---------- 
        datetime_str_series : pd.Series
            Contains military times 
        
        Returns
        -------
        pd.Series
            Str representation of standard datetime 
        """
        
        # Drop empty columns so you don't get an index out of range error 
        datetime_str_pm = datetime_str_series.replace('', np.nan).dropna()
        
        period = 'AM'
        for datetime_str in datetime_str_pm:  
            
            datetime_str_list = datetime_str.split()
            date = datetime_str_list[0]
            time = datetime_str_list[1]
            time_list = time.split(':')
            
            # Grab the hours
            hours = int(time_list[0])
            if (hours == 12): 
                period = 'PM'
            if (hours > 12): 
                hours = str(hours-12)
            
            # Grab the minutes
            minutes = time_list[1]

            # Grab the seconds 
            if (len(time_list) == 3): 
                seconds = time_list[2]
            else: 
                seconds = '00'
            
            # Replace
            new_str = date + ' ' + str(hours) + ':' +  minutes + ':' +  seconds + ' ' + period  
            datetime_str_series.replace(datetime_str, new_str, inplace=True)
        return datetime_str_series

    def map_columns(self) -> pd.DataFrame: 
        """Returns a dataframe that contains only the CSV columns that will be mapped
        to the output files. 
        """

        title_inputs =  self.mapped_settings.get_column('Input')
        new_titles = self.mapped_settings.get_column('Title')
        range_inputs = self.mapped_settings.get_column('Range')
        format = self.mapped_settings.get_column('Format')
        raw_data = self.df.copy()
    
        # Initialize the dataframe that store the mapped values 
        mapped_df = pd.DataFrame()
        
        # Find size of dataframe column  
        max_size = raw_data.iloc[:,0].size
        
        # Determine the column with the largest range interval, whose index will be used for the entire dataframe. 
        interval_index = self._largest_interval(range_inputs, max_size)
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
    
    def _round_numbers(self, series, round_to) -> pd.Series: 
        """ Round numbers in the series to the number of decimal places indiciated by 'round_to.'"""

        series = series.round(round_to)
        return series
    
    def _largest_interval(self, range_inputs, max_size):
        """Determines the CSV column with the largest set interval. 

        Parameters
        ---------- 
        range_inputs : pd.Series
            Interval of data set we want read into each processed CSV column
        max_size : int 
            Size of the CSV column 

        Returns
        ------- 
        int
            Row label of the CSV column with the largest set interval 
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
        """Gives the starting and ending row index of the column's data interval. 

        Parameters
        ---------- 
        current_range : float
            The interval of the data to be read in 'start:end' format (inclusive)
        max_size : int
            Size of the CSV column 

        Returns
        ------- 
        list
            First element gives the starting row index, second element gives the ending row 
            index
        """
        
        start = 0 
        end = max_size
 
        if (pd.isnull(current_range)): 
            pass
        else: 
            range_list = current_range.split(':')
            
            # Start at the very beginning and stop at a specific line number
            if (range_list[0] == ''):
                end = int(range_list[1])
            
            # Start at a specific line number and go to the very end 
            elif (range_list[1] == ''): 
                start = int(range_list[0]) - 1 #- self.get_startRow()
            
            # Start and stop at specific line numbers
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
        """Returns output_df with the str representations of datetime objects converted into 
        timedelta objects. 
        
        Parameters
        ---------- 
        output_df : pd.DataFrame
            Contains only the colums we want processed in the CSV  

        Returns
        ------- 
        pd.DataFrame
            Time columns are converted into elapsed times
        """ 

        # Grab the time units of the columns whose values is to be converted into elapsed times 
        time_units_df = self.mapped_settings.get_column('Time Unit').dropna()

        # If there are time values that need to be reformatted...
        if (not time_units_df.empty): 
            
            # 'index' contains the indices of the time columns in mapped_settings ('Sheet 1' of the configuration file) 
            all_time_indices = time_units_df.index.values
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
        """Converts the values in a series into str representations of timedelta objects.  

        Helper function to convert_to_elapsed_time(). 

        Parameters
        ---------- 
        series : pd.Series
            The CSV column that is to be converted. Will either contain floats 
            or a str representation of a datetime object in %m/%d/%Y %H:%M:%S AM/PM format. 
        unit : str
            The unit of time of the CSV column. D = datetime, H = hours, M = minutes, 
            S = seconds

        Returns
        ------- 
        pd.Series 
            Contains a str representation of a timedelta object in %H:%M:%S format 
        """

        series = series.dropna()

        #FIXME: Takes up too much space 
        # Creating a copy of 'series' to be iterated over. That way even if two cells have the same datetime, 
        # and both cells are replaced in the original 'series,' the for loop will not break when we iterate 
        # over the second copy.  
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
        """Splits a single time unit into its hours, minutes, and seconds. 

        Takes in a float representation of a a single unit of time, converts it into an integer, and 
        returns a list of the original time in %H:%M:%S format. 

        Helper function to convert_to_elapsed_times(). 

        Parameters
        ---------- 
        time : float 
            Given time to be converted
        time_unit : str
            The unit of time that the given 'time' is in

        Returns: 
        list
            Holds the hours, minutes, and seconds of the given 'time' 
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
        """Converts values in a series into timedelta objects. 

        Helper function to convert_to_elapsed_times(). 

        Parameters
        ----------
        time_series : pd.Series
            Contains str representations of timedelta objects.  
        start_time : str
            Str representation of starting time in the original dataframe

        Returns
        ------- 
        None  
        """

        time_series_modified = time_series.dropna()
        start_time = pd.to_timedelta(start_time)

        # Iterate through 'time_series_modified' which has the NaN values dropped. 
        # Should still replace the str representation with the timedelta object in 
        # the original 'time_series'
        for current_time in time_series_modified: 
            
            # Convert the str 'current_time' into a timedelta object and find the difference between 'current_time' and 'start_time'
            # to find the elapsed time. Convert the difference between the two times into a str and use the space 
            # delimiter to split it into a list. 
            difference= str(pd.to_timedelta(current_time)-start_time)
            difference_list = difference.split()
            
            # Store the time portion of the str into 'elapsed_time' and use the colon delimiter to 
            # split the time into a list.  
            elapsed_time = difference_list[2]
            elapsed_time_list = elapsed_time.split(':')
            
            # Convert each element in the list into an integer and use the elements to produce a timedelta object 
            time = timedelta(hours = int(elapsed_time_list[0]), minutes = int(elapsed_time_list[1]), seconds = int(elapsed_time_list[2]))            
            
            # Replace 'current_time' with 'time' in 'time_series'
            time_series.replace(current_time, time, inplace = True)
    

    
            

   