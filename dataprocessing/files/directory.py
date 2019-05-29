import os 
from .file import File, ChartFile
from .file_types import ExcelFile
#from .file_types import ExcelFile, JPEGFile, PDFFile, TXTFile
class Directory(ExcelFile): 

    def __init__(self, excel_file): #, jpeg_file, pdf_file, txt_file): 
        # TODO: call superconstructor here 
        self.directory = None 
        self.excel_file = excel_file 
        #self.jpeg_file = jpeg_file
        #self.pdf_file = pdf_file 
        #self.txt_file = txt_file

    def create(self): 
        self.make()
        self.fill()

    def make(self): 
        directory_path = os.getcwd() + '\\' + 'output'
        if (os.path.isdir(directory_path)): 
            for file in os.listdir(directory_path): 
                print(file)
                os.remove(file)
        else: 
            os.mkdir(directory_path)
    
    def fill(self): 
        if super().will_output_files():
            self.excel_file.get_name()

    

