import os 
import shutil

class Directory(object):
    """
    Creates a subdirectory in the current directory to store 
    the Excel version of the CSV file and all output files. 

    If the directory already exists, it will be overwritten. 
    
    Attributes
    ----------
    directory_path: str
        File path of the directory
    raw_data_file : str
        Filename of raw data files 
    excel_file : str
       Filename of excel output file 
    jpeg_file : str
        Filename of jpeg output file  
    pdf_file : str
        Filename of pdf output file 
    txt_file: str 
        Filename of txt output file
    """ 

    def __init__(self, output_name, raw_data_file, excel_file, jpeg_file, pdf_file, txt_file): 
        self.directory_path = os.path.join(os.getcwd(), output_name) 
        self.raw_data_src = os.path.join(os.getcwd(), raw_data_file)
        self.excel_src = os.path.join(os.getcwd(), excel_file)
        self.jpeg_src = os.path.join(os.getcwd(), jpeg_file)
        self.pdf_src = os.path.join(os.getcwd(), pdf_file)
        self.txt_src = os.path.join(os.getcwd(), txt_file)

    def create(self): 
        """Make directory and move files."""

        self._make()
        self._move_files()

    def _make(self): 
        """
        Create a directory. If the directory already exists, delete it.
        
        Helper function to create().
        """

        if (os.path.isdir(self.directory_path)): 
            shutil.rmtree(self.directory_path)
        
        os.mkdir(self.directory_path)
    
    def _move_files(self): 
        """
        Moves the Excel CSV file and all output files into the directory.
        
        Helper function to _move_files(). 
        """

        # Move Excel raw data file into directory 
        shutil.move(self.raw_data_src, self.directory_path)

        # Move Excel output file into directory, if it exists  
        exists = os.path.isfile(self.excel_src)
        if (exists): 
            shutil.move(self.excel_src, self.directory_path)

        # Move JPEG output file into directory, if it exists 
        exists = os.path.isfile(self.jpeg_src)
        if (exists): 
            shutil.move(self.jpeg_src, self.directory_path)
        
        # Move PDF output file into directory, if it exists 
        exists = os.path.isfile(self.pdf_src)
        if (exists): 
            shutil.move(self.pdf_src, self.directory_path)
        
        # Move txt output file into directory, if it exists
        exists = os.path.isfile(self.txt_src)
        if (exists): 
            shutil.move(self.txt_src, self.directory_path)
        

    


    

