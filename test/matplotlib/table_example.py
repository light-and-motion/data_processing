import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import random 

#https://stackoverflow.com/questions/19726663/how-to-save-the-pandas-dataframe-series-data-as-a-figure
#https://stackoverflow.com/questions/17542524/pandas-dataframes-in-reportlab
#http://pandas.pydata.org/pandas-docs/version/0.15/visualization.html#visualization-table

## Padding: https://stackoverflow.com/questions/44798364/matplotlib-text-alignment-in-table
# https://stackoverflow.com/questions/35634238/how-to-save-a-pandas-dataframe-table-as-a-png
df = data = pd.DataFrame([[random.random() for i in range(1,4)] for j in range (1,100)])
#df = pd.DataFrame([1])
print(df.size)


# Assuming that you have a dataframe, df
pp = PdfPages('Appendix_A.pdf')
total_rows, total_cols = df.shape; #There were 3 columns in my df

rows_per_page = 30 # Assign a page cut off length
rows_printed = 0
page_number = 1

#fig = plt.figure(figsize=(8.5,11))
#ax = plt.subplot(111)
while (total_rows >0): 
       #put the table on a correctly sized figure    
       #fig=plt.figure(figsize=(8.5, 11))
       fig = plt.figure(figsize=(8.5,11))
       ax = plt.subplot()
       ax.axis('off')
       #print(df.iloc[rows_printed: rows_printed+rows_per_page])
       matplotlib_tab = pd.plotting.table(ax,df.iloc[rows_printed:rows_printed+rows_per_page], loc='upper center') #, colWidths=[0.2, 0.2, 0.2])    
       
       #pd.plotting.table.auto_set_font_size(True)
       # Give you cells some styling 
       table_props=matplotlib_tab.properties()
       table_cells=table_props['child_artists'] # I have no clue why child_artists works
       for cell in table_cells:
              cell.set_height(0.024)
              cell.set_fontsize(12)
              
              

       # Add a header and footer with page number 
       fig.text(4.25/8.5, 10.5/11., "Table", ha='center', fontsize=12)
       fig.text(4.25/8.5, 0.5/11., str(page_number), ha='center', fontsize=12)

       pp.savefig()
       plt.close()

       #Update variables
       rows_printed += rows_per_page
       total_rows -= rows_per_page
       page_number+=1

pp.close()
