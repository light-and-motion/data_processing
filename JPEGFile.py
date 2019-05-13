from File import ChartFile
import pandas as pd
from datetime import (datetime, time)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class JPEGFile(ChartFile): 
    def output_JPEG(self): 
        jpeg_choice = self.make_file(self.general_settings.get_column('JPEG').loc[0])
        pdf_choice = self.make_file(self.general_settings.get_column('PDF').loc[0])
        if ((jpeg_choice or pdf_choice) and self.make_chart()):
            self.make_jpeg(jpeg_choice, pdf_choice) 
    
    def make_jpeg(self, jpeg_choice, pdf_choice):  
        """Produces a JPG and/or PDF file of a matplotlib chart

        Parameters: 
        jpeg_choice (bool): True if chart will be saved as JPEG, False otherwise
        pdf_choice (bool): True if chart will be saved as PDF, False otherwise
        """
        
        new_titles = self.mapped_settings.get_column('Title')
        chart_title = self.general_settings.get_column('Chart Title')
        x_axis_index = self.get_x_axis().index[0]
        y_axis_indices = self.get_y_axis().index

        # Plot multiple lines on a single chart. 
        # As matplotlib does not allow timedelta objects to be directly set as an axis, must convert to a 
        # datetime object to plot on chart. 
        x_axis = self.output_data[new_titles[x_axis_index]].dropna() #mapping_df[new_titles[x_axis_row.index[0]]].dropna() 
        if (not (pd.isnull(self.mapped_settings.get_column('Time Unit').loc[x_axis_index]))):
            x_axis = pd.Series(self.convert_timedelta_to_datetime(x_axis))
            
        
        #TODO: ReminderIf there are multiple y-axes, their dtypes have to be the same! 
        #TODO: Why does the data range have to be the same even columns that will not be plotted
        fig, ax = plt.subplots(1,1)

        print(self.output_data)
        for y_axis_index in y_axis_indices: 
            y_axis_title = new_titles[y_axis_index]
            y_axis = self.output_data[y_axis_title]
            if (not pd.isnull(self.mapped_settings.get_column('Time Unit').loc[y_axis_index])): 
                y_axis = pd.Series(self.convert_timedelta_to_datetime(y_axis))
            plt.plot(x_axis, y_axis, label = new_titles.iloc[y_axis_index])
       
        
        # Set the x-label and the y-label/legend
        self.chart_legend(plt, x_axis_index, y_axis_indices)
        
        # Set the title 
        title = self.chart_title(new_titles, chart_title, x_axis_index, y_axis_indices)
        plt.title(title)
        
        # Set gridlines 
        self.grid_lines(plt)   

        # Chart scaling 
        self.chart_scaling(plt)
        
        # Save charts in stated formats
        
        if (jpeg_choice): 
            plt.savefig(self.output_name + '.jpeg')
        
        if (pdf_choice): 
            plt.savefig(self.output_name + '_chart' + '.pdf') 
        #return fig
        

    #TODO: Faster way to acomplish this https://stackoverflow.com/questions/48294332/plot-datetime-timedelta-using-matplotlib-and-python
    def convert_timedelta_to_datetime(self,timedelta_series): 
        """Takes in a Series that contains timedelta objects and returns a Series that contains datetime objects"""
        
        # Convert 'timedelta_series' to type str 
        timedelta_str_series = timedelta_series.astype(str)
        #print(timedelta_str_series)

        # Split 'timedelta_str_series' using the space delimiter and store the results into a list
        timedelta_str_list = [time.split() for time in timedelta_str_series]
        
        # Retrieve the 'time' portion of 'timedelta_str_list' and store into another list  
        time_str_list = [time[2] for time in timedelta_str_list]
    
        # Split 'time_str_list' using '.' delimiter and store results back into 'time_str_list'  
        time_str_list = [time.split('.') for time in time_str_list]

        # Retrieve the '%H:%M:%S' formatted time and store results back into list 
        time_str_list = [time[0] for time in time_str_list]

        # Convert 'time_str_list' into a series and turn each element into a datetime.time() object. 
        # Store in a new list. 
        time_str_series = pd.Series(time_str_list)
        time_obj = [datetime.strptime(time_str, '%H:%M:%S').time() for time_str in time_str_series]
        x_axis = [ datetime.combine(datetime.now(), time) for time in time_obj]
        
        return x_axis

    def chart_legend(self, plt, x_axis_index, y_axis_indices): 
        # Set the labels and/or legend of the chart
        
        new_titles = self.mapped_settings.get_column('Title') 
        plt.xlabel(new_titles[x_axis_index])
        if (len(y_axis_indices) > 1):
            plt.legend(loc='best')
        else: 
            plt.ylabel(new_titles[y_axis_indices[0]])

    def grid_lines(self, plt): 
        isGridLinesOn = self.general_settings.get_column('Grid Lines') 
        if (pd.isnull(isGridLinesOn.loc[0]) or isGridLinesOn.loc[0].upper() == 'YES'): 
            plt.grid(b = True)
    
    def format_date(self, fig, ax): 
        if (not self.mapped_settings.get_column('Time Unit').dropna().empty):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            fig.autofmt_xdate()
    
    def chart_scaling(self, plt): 
        x_min = self.general_settings.get_column('X Min').loc[0]
        x_max = self.general_settings.get_column('X Max').loc[0]
        y_min = self.general_settings.get_column('Y Min').loc[0]
        y_max = self.general_settings.get_column('Y Max').loc[0]

        if (not pd.isnull(x_min)): 
            plt.xlim(left = x_min)
        if (not pd.isnull(x_max)): 
            plt.xlim(right = x_max)
        if (not pd.isnull(y_min)): 
            plt.ylim(bottom = y_min)
        if (not pd.isnull(y_max)): 
            plt.ylim(top = y_max)
        


    
