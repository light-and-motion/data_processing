import unittest
from datetime import timedelta
import pandas as pd
import numpy.testing as npt
import timedelta
class TestConversion(unittest.TestCase): 
    def setUp(self): 
        self.config = pd.read_excel('timedelta/Config.xlsx')
        self.df = pd.read_csv('timedelta/test.csv')
        self.df['ElapsedTime'] = pd.to_timedelta(self.df['ElapsedTime'])
    def test_timedelta_2_str(self): 
        npt.assert_array_equal(timedelta.timedelta_to_string(self.config, self.df).to_numpy() , self.df['ElapsedTime2'].to_numpy())

if __name__ == '__main__': 
    unittest.main()

