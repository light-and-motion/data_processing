import pandas as pd

class File(object): 
    def __init__(self, mapped_settings, general_settings, output_data, output_name): 
        self.mapped_settings = mapped_settings
        self.general_settings = general_settings
        self.output_data = output_data
        self.output_name = output_name
    
    def make_file(self, choice): 
        """ Determines if an Excel, JPEG, or PDF file will be generated"""

        if (pd.isnull(choice) or choice.upper() == 'YES'): 
            return True
        return False

class ChartFile(File): 
    def make_chart(self):
        """Returns a list that indicates whether there will be a chart and if so, which columns will serve as the x-axis 
        and y-axis 

        Parameters: 
        axis (series): Indicates which CSV columns will serve as the x-axis and the y-axis

        Returns:
        List: 
            a) If first element is False, no chart will be generated
            b) If first element is True, second element will be a one-element series of the column that will serve as the x-axis 
                and third element will be a series of the column(s) that will serve as the y-axis
        """ 
        axis = self.mapped_settings.get_column('Axis')
        if (axis.dropna().empty or not ((axis == 'x').any() or (axis == 'X').any()) or not ((axis == 'y').any() or (axis == 'Y').any())):  
            return False
        return True
 
    def get_x_axis(self): 
        x_axis = None
        if (self.make_chart()): 
            axis = self.mapped_settings.get_column('Axis')
            x_axis = axis.loc[(axis == 'x') | (axis == 'X')]
        return x_axis
    
    def get_y_axis(self): 
        y_axis = None
        if (self.make_chart()): 
            axis = self.mapped_settings.get_column('Axis')
            y_axis = axis.loc[(axis == 'y') | (axis == 'Y')]
        return y_axis        
    
    def get_chart_title(self, new_titles, chart_title, x_axis_index, y_axis_indices):
        """Returns the chart title. 

        If no title is given, then the chart title will default to the format '[All] y-axis vs x-axis'
        
        Parameters: 
        new_titles (series): New titles of the processed CSV columns 
        chart_title (series): Contain a manually given chart title or NaN
        x_axis_row (series): Index location of the column to serve as the x_axis
        y_axis_row (series): Index location(s) of the column(s) to serve as the y-axis 
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


