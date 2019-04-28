
from openpyxl import load_workbook
class User_Interface:
    def __init__(self, choice, config_file, input_csv, output_name):
        self.choice = choice
        self.config_file = config_file
        self.input_csv = input_csv
        self.output_name = output_name

# ENCAPSULATE INTO ANOTHER CLASS 
#Prints program banner
def banner():
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
    #config_file = 'LumenConfig'
    config_file = 'TestTimeConfig'
    return [load_workbook(config_file + '.xlsx'), config_file]


#Asks user for file name of CSV to process
#default is original Lumensphere data (testing purposes)
def choose_csv():
    input_csv = None
    while input_csv == None:
        csv_choice = input('Enter name of CSV file to process: ')
        input_csv = csv_choice
    #input_csv = 'Lumen_T'
    input_csv = 'Test_Time'
    #input_csv = 'Lumen_1'
    return input_csv


##asks user for file name of final excel workbook
#default is LumenData (testing purposes)
def choose_output_name():
    output_name = None
    while output_name == None:
        output_choice = input('Enter name of Output file: ')
        output_name = output_choice
    output_name = 'LumenData'
    return output_name
