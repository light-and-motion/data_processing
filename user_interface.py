from openpyxl import load_workbook
class User_Interface:
    """A class that serves as the text-based user interface"""

def banner():
    """Prints a banner to indicate start of program"""

    print('*****************************')
    print('*  Data Processing Program  *')
    print('*****************************')

def choose_config(choice):
    """Returns a list that contains the workbook itself as well as the name of the configuration file"""
    choice = 1
    if choice == 1:
        config_file = input('Enter name of Lumensphere config file: ')
    elif choice == 2:
        config_file = input('Enter name of Multimeter config file: ')
    elif choice == 3:
        config_file = input('Enter name of Serial Data config file: ')
    #config_file = 'MultiMeterConfig'
    config_file = 'LumenConfig'
    #config_file = 'TestTimeConfig'
    #config_file = 'ColorMetricsConfig'
    return [load_workbook(config_file + '.xlsx'), config_file]


def choose_csv():
    """Asks the user for file name of the CSV"""

    input_csv = None
    while input_csv == None:
        csv_choice = input('Enter name of CSV file to process: ')
        input_csv = csv_choice
    #input_csv = 'Temp_2'
    input_csv = 'Lumen_T'
    #input_csv = 'Test_Time'
    #input_csv = 'Lumen_1'
    #input_csv = 'ColorMetrics_1'
    return input_csv

def choose_output_name():
    """Asks user to input the name of the output file"""

    output_name = None
    while output_name == None:
        output_choice = input('Enter name of Output file: ')
        output_name = output_choice
    #output_name = 'MultiMeterData'
    output_name = 'LumenData'
    #output_name = 'ColorMetricsData'
    return output_name
