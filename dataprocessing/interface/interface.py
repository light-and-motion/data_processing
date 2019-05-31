from openpyxl import load_workbook
class UserInterface (object):
    """A class that serves as the text-based user interface"""

    @staticmethod
    def banner():
        """Prints a banner to indicate start of program"""

        print('*****************************')
        print('*  Data Processing Program  *')
        print('*****************************')

    def choose_config(self):
        """Returns a list that contains the workbook itself as well as the name of the configuration file"""
        config_file = input('Enter name of configuration file: ')

        return [load_workbook(config_file + '.xlsx'), config_file]


    def choose_csv(self):
        """Asks the user for file name of the CSV"""

        input_csv = None
        while input_csv == None:
            csv_choice = input('Enter name of CSV file to process: ')
            input_csv = csv_choice

        return input_csv

    def choose_output_name(self):
        """Asks user to input the name of the output file"""

        output_name = None
        while output_name == None:
            output_choice = input('Enter name of Output file: ')
            output_name = output_choice
        
        return output_name