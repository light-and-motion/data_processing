import unittest
import pandas as pd
from fixtures.datetime.functions import search_for_military_times, date_parser
import numpy.testing as npt

class TestZeroSeconds(unittest.TestCase): 
    def setUp(self): 
        # Load test data
        #self.df = pd.read_csv(r'C:\Users\Cathy Hsu\Light and Motion\data_processing\tests\fixtures\test_datetime_zero.csv')
        self.df = pd.read_csv('fixtures/datetime/test_datetime_zero.csv')
    def test_count(self): 
        self.assertEqual(self.df.size, 6)
    def test_type(self): 
        self.assertEqual(type(self.df['StartTime1']), pd.Series)
    def test_column_label(self): 
        self.assertEqual(self.df.columns[0], 'StartTime1')
    def test_search_for_military_times(self): 
        self.assertEqual(search_for_military_times(self.df), ['StartTime1'])
    def test_date_parser(self): 
        npt.assert_array_equal(date_parser(self.df['StartTime1']).to_numpy(), self.df['StartTime2'].to_numpy())
    
class TestNonzeroSeconds(unittest.TestCase): 
    def setUp(self): 
        self.df = pd.read_csv('fixtures/datetime/test_datetime_nonzero.csv')
    def test_search_for_military_times(self): 
        self.assertEqual(search_for_military_times(self.df), ['StartTime1'])
    def test_date_parser(self): 
        npt.assert_array_equal(date_parser(self.df['StartTime1']).to_numpy(), self.df['StartTime2'].to_numpy())


class TestMicroSeconds(unittest.TestCase): 
    def setUp(self): 
        self.df = pd.read_csv('fixtures/datetime/test_datetime_microseconds.csv')
    def test_search_for_military_times(self): 
            self.assertEqual(search_for_military_times(self.df), ['StartTime1'])
    def test_date_parser(self): 
        npt.assert_array_equal(date_parser(self.df['StartTime1']).to_numpy(), self.df['StartTime2'].to_numpy())



if __name__ == '__main__': 
    unittest.main()
    