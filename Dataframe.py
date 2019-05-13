import pandas as pd
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
    """A class that processes the mapped settings of the configuration file"""
    
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
        data = self._letter2int(super().get_column('Input Column Numbers'))
        super().set_column('Input Column Numbers', data)

        data = self._letter2title(super().get_column('Input'), col_labels)
        super().set_column('Input', data)

        data = self._letter2int(super().get_column('Output'))
        super().set_column('Output', data)

        data = self._default_titles(super().get_column('Title'), super().get_column('Input'))
        super().set_column('Title', data)

    def _letter2title(self, letter_series, names):
        """Returns a series where column letters are converted into column titles.

        Parameters: 
        letter_series (series): Excel column letters
        names (series): CSV column titles 
        """
        col_title = []
        indices = self._letter2int(letter_series)
        
        for x in range(letter_series.size): 
            index = indices.loc[x]      
            title = names[index-1]
            col_title.append(title)
        
        return pd.Series(col_title)
    
    def _letter2int(self, letter_series):
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
    
    def _default_titles(self, new_titles, input_titles): 
        """Returns a series where processed CSV columns that are not given a new title in output
        now hold their original CSV column titles. 
        """
        
        x = 0
        for title in new_titles: 
            if (pd.isnull(title)): 
                new_titles.iat[x] = input_titles.iat[x]
            x += 1
        return new_titles

