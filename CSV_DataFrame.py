from Dataframe import DataFrame
import pandas as pd
import numpy as np
from datetime import datetime

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
        
    def create_dataframe(self): 
        """Returns a dataframe of the CSV file 

        Parameters: 
        file (str): Name of CSV file to be processed
        general_settings_2 (dataframe): 'General Settings' of the configuration file 
        """

        start_ser = self.general_settings.get_column('Start Row')
        stop_ser = self.general_settings.get_column('Stop Row')
        skip_ser = self.general_settings.get_column('Skip Row')
        transpose_ser = self.general_settings.get_column('Transpose')
        
        # Default values         
        startLine = 0
        stopLine = None
        skipLine = None
        transpose = "NO"


        if (not start_ser.dropna().empty): 
            startLine = start_ser.loc[0]-1
        if (not stop_ser.dropna().empty): 
            stopLine = stop_ser.loc[0]-startLine-1
        if (not skip_ser.dropna().empty):
            skipLine = skip_ser.loc[0]
        if (not transpose_ser.dropna().empty): 
            transpose = transpose_ser.loc[0]

        # Read the CSV into the dataframe     
        self.df = self.df.append(self._read_csv_type(startLine, stopLine, skipLine, transpose)) 
        
        ###
        if (transpose.upper() == 'YES'): 
            #TODO: Ask if N/A marker is to be kept or if the cells that contain it be empty instead. 
            self.df = self._transpose(startLine, skipLine)
        
        ## Minus 1 is added because old column of transposed df has been dropped 
        if (not skipLine == None): 
            self.df.drop(skipLine-startLine-1, inplace=True)

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
        
    def _read_csv_type(self, startLine, stopLine, skipLine, transpose):
        """Returns the prototype dataframe of the CSV file 
        
        Parameters: 
        file (str):  Name of CSV file to be processed
        startLine (int): Row to begin processing CSV file
        stopLine (int): Row to stop processing CSV file
        skipLine (int): Line you want to skip when processing CSV file. Has to be between startLine and stopLine
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
        else: 
            return pd.read_csv(self.file_name + '.csv', 
                            header = None, 
                            index_col= None, 
                            skiprows= startLine,
                            nrows = stopLine,  
                            keep_default_na = False, 
                            encoding = 'ISO-8859-1') 

    
    def _transpose(self, startLine, skipLine): 
            """
            Returns a transposed df 

            Parameters: 
            df (df): df that is to be transposed
            startLine (int): Row to begin processing CSV file
            skipLine (int): Line you want to skip when processing CSV file. Has to be between startLine and stopLine
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
        end = max_size-1

        # Range is calculated against the row indexes of the Excel worksheet. Thus, the first
        # cell in a column will be located in row 2.   
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
    
   