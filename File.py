import pandas as pd

class File(object): 
    """
    A class used to output files of the processed CSV. 

    Attributes
    ---------- 
    mapped_settings: MappedExcelDataFrame 
        Contains the mapped settings in the configuration file
    general_settings: ExcelDataFrame
        Contains the general settings of the configuration file  
    output_data: pd.DataFrame 
        Dataframe of the processed CSV 
    output_name: str 
        Name of the output files 
    """

    def __init__(self, mapped_settings, general_settings, output_data, output_name): 
        self.mapped_settings = mapped_settings
        self.general_settings = general_settings
        self.output_data = output_data
        self.output_name = output_name
    
    def make_file(self, choice) -> None: 
        """ Determines if an Excel, JPEG, or PDF file will be generated"""

        if (pd.isnull(choice) or choice.upper() == 'YES'): 
            return True
        return False
    
    def get_str_timedelta(self): 
        """Convert timedelta objects into str representations."""

        new_df = self.output_data.fillna(' ')
        indices = self.mapped_settings.get_column('Time Unit').dropna().index
        for i in indices: 
            label = self.mapped_settings.get_column('Title').loc[i]
            new_df[label] = [time[7:15] for time in new_df[label].astype(str)]
        return new_df

class ChartFile(File): 
    """
    Extends File to output files that contain a chart. 
    """

    def make_chart(self) -> bool:
        """Returns True if a chart will be generated, False if not.""" 

        axis = self.mapped_settings.get_column('Axis')
        if (axis.dropna().empty or not ((axis == 'x').any() or (axis == 'X').any()) or not ((axis == 'y').any() or (axis == 'Y').any())):  
            return False
        return True
 
    #TODO: Determine if get_x_axis() and get_y_axis() return the indices only? 
    def get_x_axis(self) -> pd.Series: 
        """
        Returns a series of length 1 that contains the row index of the 
        x-axis column label in the configuration file mapped_settings. 
        """
        
        x_axis = None
        if (self.make_chart()): 
            axis = self.mapped_settings.get_column('Axis')
            x_axis = axis.loc[(axis == 'x') | (axis == 'X')]
        return x_axis
    
    def get_y_axis(self) -> pd.Series: 
        """
        Returns a series that contains the row indices of the
        y-axis column labels in the configuration file mapped_settings. 
        """ 
        
        y_axis = None
        if (self.make_chart()): 
            axis = self.mapped_settings.get_column('Axis')
            y_axis = axis.loc[(axis == 'y') | (axis == 'Y')]
        return y_axis        
    
    def get_chart_title(self, new_titles, chart_title, x_axis_index, y_axis_indices):
        """Determines the chart title. 

        If no title is given, then the chart title will default to the format '[All] y-axis vs x-axis.'
        
        Parameters
        ---------- 
        new_titles : series 
            New titles of the processed CSV columns 
        chart_title : series
            Contains a manually given chart title or NaN
        x_axis_row : series 
            Row index of the x-axis column label in the configuration file
        y_axis_row : series 
            Row indices of the y-axis column labels in the configuration file

        Returns
        -------
        str
            Title of the chart  
        """
        
        # Note: A column with 'NaNs' is not considered empty
        if (chart_title.dropna().empty): 
            title = ''
            for i in range(y_axis_indices.size-1): 
                title += new_titles.loc[y_axis_indices[i]] + ", "
            title += new_titles.loc[y_axis_indices[y_axis_indices.size-1]] + " vs " + new_titles.loc[x_axis_index]
        else: 
            title = chart_title.loc[0]
        return title


