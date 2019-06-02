import os 
from openpyxl import Workbook

excel = Workbook()

print (os.getcwd())
directory_path = os.getcwd() + r'\output'


if (os.path.isdir(directory_path)): 
    for file in os.listdir(directory_path): 
        print(file)
        os.remove(file)
else: 
    os.mkdir(directory_path)
excel.save(directory_path + r'\Workbook1.xlsx')
#excel.save(directory_path + r'\Workbook2.xlsx')
