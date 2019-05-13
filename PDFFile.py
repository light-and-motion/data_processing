from File import File, ChartFile 
import pdfkit
from PyPDF2 import PdfFileReader, PdfFileWriter
import os
class PDFFile (ChartFile): 

    def output(self): 
        pdf_choice = self.make_file(self.general_settings.get_column('PDF').loc[0])
        if (pdf_choice): 
            self.make_pdf()
    
    def make_pdf(self): 
        """Generates a pdf of the processed results 

        Parameters: 
        output_name (str): Name PDF will be saved as 
        mapping_data_df (dataframe): CSV columns to be processed
        create_chart (bool): True if a chart will be generated in the PDF, False if not 
        """
        
        # Get the file path of the wkhtmltopdf executable 
        #config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        df_file = os.getcwd() + '\\' + self.output_name + '.pdf'
        
        # Replace NaN values with empty strings so the empty data cells do not look like they hold any values in the PDF file 
        mapping_df = self.output_data.fillna('')
        
        # If the PDF file is to contain a chart, then merge the dataframe and chart PDF into a single PDF. 
        # Otherwise, just save the dataframe PDF as is. 
        if (not self.make_chart()): 
            pdfkit.from_string(mapping_df.to_html(), df_file)
    
        else:  
            df_file = os.getcwd() + '\\' + self.output_name + '_table.pdf'
            pdfkit.from_string(mapping_df.to_html(), df_file)
            paths = [os.getcwd() + '\\' + self.output_name + '_chart.pdf' ,df_file]
            self.merge_pdfs(paths)

    def merge_pdfs(self,paths): 
        """Merges two PDFs into a single PDF 
        
        Source: https://realpython.com/pdf-python/

        Parameters: 
        paths (list): File paths of the PDFs to be merged  
        output_name (str): Name PDF will be saved as  
        """
        
        pdf_writer = PdfFileWriter()

        for path in paths: 
            pdf_reader = PdfFileReader(path)
            for page in range(pdf_reader.getNumPages()):
                pdf_writer.addPage(pdf_reader.getPage(page))
        
        with open(self.output_name + '.pdf', 'wb') as out: 
            pdf_writer.write(out)
        
        # Delete merged files 
        os.remove(paths[0])
        os.remove(paths[1])