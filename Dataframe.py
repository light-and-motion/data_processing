import pandas as pd
import numpy as np
from datetime import datetime
class DataFrame(object): 
    """
    A class used to read a file into a pd.df

    Attributes: 
    file_name (str): Name of file to be read into CSV 
    df (pd.df): Stores file_name contents 
    """
    def __init__(self,file_name, df):
        self.file_name = file_name
        self.df = pd.DataFrame()

    def print_df(self): 
        print(self.df)
    
    def print_dtypes(self): 
        print(self.df.dtypes)
    
    def get_df(self): 
        return self.df

    def get_column(self, column_name): 
        return self.df[column_name]
    
    #TODO: What does @property do???
    @property
    def get_column_labels(self): 
        return self.df.columns
    
    def set_column(self,column_name, data_list):
        self.df[column_name] = data_list
    

class ExcelDataFrame (DataFrame): 
    """ 
    A class used to read an Excel file into a pd.df

    Attributes: 
    sheet_name (str) = Name of sheet in file_name we want read into a pd.df
    """
    def __init__(self, file_name, df, sheet_name): 
        super().__init__(file_name, df)
        self.sheet_name = sheet_name
    
    def create_dataframe(self): 
        """Returns a dataframe of an Excel file 

        Used to store configuration data into a dataframe. 

        Parameters: 
        file (str): Name of Excel file  
        sheet (str): Name of Excel sheet from 'file'  
        """
        self.df = self.df.append(pd.read_excel(self.file_name + '.xlsx', sheet_name = self.sheet_name, dtype = {'Title': str}))
    
class MappedExcelDataFrame(ExcelDataFrame): 

    def format(self, col_labels):
        """Alters several settings of the configuration dataframe. 
        Changes: 
            a) Column letters in 'Input' have been replaced by column titles of the given CSV columns
            b) Column letters in 'Output' have been replaced by column numbers of the given CSV columns 
            c) Empty column titles in the 'title' column have been filled in with original titles of the CSV columns 

        Parameters:  
        col_labels (series): Original labels of the CSV columns 
        """
        
        # TODO: Research super() https://realpython.com/python-super/
        super().set_column('Input Column Numbers', super().get_column('Input').str.upper())
        
        data = self.letter2title(super().get_column('Input'), col_labels)
        super().set_column('Input', data)

        data = self.letter2int(super().get_column('Output'))
        super().set_column('Output', data)

        data = self.default_titles(super().get_column('Title'), super().get_column('Input'))
        super().set_column('Title', data)

    def letter2title(self, letter_series, names):
        """Returns a series where column letters are converted into column titles.

        Parameters: 
        letter_series (series): Excel column letters
        names (series): CSV column titles 
        """
        col_title = []
        indices = self.letter2int(letter_series)
        
        for x in range(letter_series.size): 
            index = indices.loc[x]      
            title = names[index-1]
            col_title.append(title)
        
        return pd.Series(col_title)
    
    def letter2int(self, letter_series):
        """Returns a series where column letters are being converted into their corresponding column number. 

        Source: https://www.geeksforgeeks.org/find-excel-column-number-column-title/

        Parameters: 
        letter_series (series): Excel column letters
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
        """Returns a series where processed CSV columns that are not given a new title in output
        now hold their original CSV column titles. 
        """
        
        x = 0
        for title in new_titles: 
            if (pd.isnull(title)): 
                new_titles.iat[x] = input_titles.iat[x]
            x += 1
        return new_titles
 
class CSVDataFrame(DataFrame): 
    """
    A class used to read a CSV file into a pd.df 

    Attributes: 
    config_df (pd.df): Contains the settings that will be used to configure csv df  
    """
    def __init__(self,file_name, df, config_df): 
        super().__init__(file_name, df)
        self.config_df = config_df
        

    def create_dataframe(self): 
        """Returns a dataframe of the CSV file 

        Parameters: 
        file (str): Name of CSV file to be processed
        config_df_2 (dataframe): 'General Settings' of the configuration file 
        """

        start_ser = self.config_df.get_column('Start Row')
        stop_ser = self.config_df.get_column('Stop Row')
        skip_ser = self.config_df.get_column('Skip Row')
        transpose_ser = self.config_df.get_column('Transpose')
        
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
        self.df = self.df.append(self.read_csv_type(startLine, stopLine, skipLine, transpose)) 
        
        ###
        if (transpose.upper() == 'YES'): 
            #TODO: Ask if N/A marker is to be kept or if the cells that contain it be empty instead. 
            self.df = self.transpose(startLine, skipLine)
        
        ## Minus 1 is added because old column of transposed df has been dropped 
        if (not skipLine == None): 
            self.df.drop(skipLine-startLine-1, inplace=True)

        # Get rid of columns with all whitespace 
        self.df = self.df.dropna('columns', how='all')

        # Reset index to start at 0 after dropping column(s)
        self.df = self.df.reset_index(drop=True)
        
        # Search for the columns that have a PM time. (Note: Excel convert str times with a PM time into 24 hour time). 
        # For example, 1:27 PM is converted into 13:27.  
        datetime_str_columns = self.search_for_pm_times()

           
        # Format the PM time columns into 12 hour time format. 
        [self.date_parser(self.df[column_name]) for column_name in datetime_str_columns]        
        
        
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
        
    def read_csv_type(self, startLine, stopLine, skipLine, transpose):
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

    
    def transpose(self, startLine, skipLine): 
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
       
    def search_for_pm_times(self):
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
        
    
    def date_parser(self, datetime_str_series):
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

    
   