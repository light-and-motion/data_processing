from openpyxl import load_workbook
class User_Interface:
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
    #elif choice == 0: #default option for testing purposes
     
    #config_file = 'LumenConfig'
    
    #else:
        #choice = None
        #print('Please enter valid input.\n')
    
    # return both the workbook and the name of the workbook in String format 
    return [load_workbook(config_file + '.xlsx'), config_file]


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






