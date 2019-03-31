from data_processing import Data_Processing
class User_interface:
    def __init__(self, choice, config_file, input_csv, output_wb):
        self.choice = choice
        self.config_file = config_file
        self.input_csv = input_csv
        self.output_wb = output_wb

# ENCAPSULATE INTO ANOTHER CLASS 
#Prints program banner
def banner():
    print('*****************************')
    print('*  Data Processing Program  *')
    print('*****************************')


#(1 = Lumensphere, 2 = Multimeter (not currently implemented), 3 = Serial Data (not currently implemented))
#Asks user to enter name of configutation file, this is to avoid having to constantly change one config file (save multiple)
def choose_config(choice):
    if choice == 1:
        config_file = input('Enter name of Lumensphere config file: ')
    elif choice == 2:
        config_file = input('Enter name of Multimeter config file: ')
    elif choice == 3:
        config_file = input('Enter name of Serial Data config file: ')
    elif choice == 0: #default option for testing purposes
        config_file = 'LumenConfig'
    else:
        choice = None
        print('Please enter valid input.\n')
    return config_file


#Asks user for file name of CSV to process
#default is original Lumensphere data (testing purposes)
def choose_csv():
    input_csv = None
    while input_csv == None:
        csv_choice = input('Enter name of CSV file to process or enter ''default'': ')
        
        if csv_choice == 'default':
            input_csv = 'Derived Data Imjin 800'
        else:
            input_csv = csv_choice
    return input_csv


##asks user for file name of final excel workbook
#default is LumenData (testing purposes)
def choose_output_wb():
    output_wb = None
    while output_wb == None:
        output_choice = input('Enter name of Output file or enter ''default'': ')

        if output_choice == 'default':
            output_wb = 'LumenData'
        else:
            output_wb = output_choice
    return output_wb
    
########################################## MAIN ####################################################################
### Main execution block ###
banner()

#Asks user for which type of data to process based on numeric input. To be passed into choose_config
data_choice = None
while data_choice == None:
    print('Which data file type would you like to process?\n1. Lumensphere\n2. Multimeter\n3. Serial Data\n')
    data_choice = int(input('Enter a number: '))

config_file = choose_config(data_choice)
input_csv = choose_csv()
output_wb = choose_output_wb()

df = Data_Processing(data_choice, config_file, input_csv, output_wb)


# Retrieve the csv file and store its contents into a dataframe 
raw_data_df = df.create_raw_dataframe()

# Read the raw dataframe into an Excel file 
raw_data_excel = df.create_raw_Excelbook(raw_data_df)

# Read the configuration file into config_df. 
config_df = df.read_config_file()
col_names = raw_data_df.columns
num_inputs= config_df['Input']
title_inputs = config_df['Input'].copy()
outputs = config_df['Output']
col_titles = config_df['Title']
formats = config_df['Format']
axis = config_df['Axis']
graph_title = config_df['Graph Title']

# ########################## Could be converted into functions 
# Convert the letter elements of inputs into integers and Strings and outputs into integers 
# so we can later use them as indices in different ways. 
for i in range(0, num_inputs.size): 
    num_inputs.replace(num_inputs.loc[i], df.letter2int(num_inputs.loc[i]), inplace = True)
    title_inputs.replace(title_inputs.loc[i], df.letter2title(title_inputs.loc[i], col_names), inplace = True)
    outputs.replace(outputs.loc[i], df.letter2int(outputs.loc[i]), inplace = True)

# output_data_df will hold all the columns that we want to plot later

# We will use col_titles_inputs as indices to extract from the raw data the columns that we want plotted
# Note: Even though only one column is being extracted at a time, the column being extracted 
# is stored in a dataframe as only dataframes, not series!, can combine with other dataframes. 

output_data_df = raw_data_df[[title_inputs.loc[0]]]


for i in range(1, num_inputs.size): 
    additional_df = raw_data_df[[title_inputs.loc[i]]]
    output_data_df = output_data_df.join(additional_df)

# format time 
output_data_df['Date/Time'] = df.time_format(output_data_df['Date/Time']) 

# create workbook to hold plotted data
output_data_wb = df.create_plotted_workbook()

# Read the output data into an Excel file
output_data_wb = df. process_data(output_data_wb, output_data_df, col_titles, num_inputs, title_inputs, outputs)

##### Chart creation 

# Call make_chart() to determine if we need to create a chart 
x_axis = df.make_chart(axis)

# If the x_axis is not empty, then create a chart 
if (x_axis.size != 0): 
    y_axis = axis.loc[(axis == 'Y') | (axis == 'y')]
    df.create_chart(output_data_wb, title_inputs, outputs, output_data_df, x_axis, y_axis, col_titles, graph_title)

#print(df.get_output_wb)
output_data_wb.save(df.get_output_wb + '.xlsx')
