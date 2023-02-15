import unittest
import pandas as pd
from pandas.testing import assert_frame_equal

from utilities.utilities import get_records_by_region


class TestMyModule(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            'region': ['A', 'B', 'C', 'A', 'B'],
            'url': ['a.com', 'b.com', 'c.com', 'd.com', 'e.com'],
            'count#': [1, 2, 3, 4, 5],
            'percent%': [20, 30, 50, 25, 75]
        })

    def test_get_records_by_region(self):
        expected_output = pd.DataFrame({
            'region': ['A', 'B', 'C'],
            'Global #': [2, 2, 1]
        }).set_index('region')
        output = get_records_by_region(self.df, 'region')
        assert_frame_equal(output, expected_output)

    def test_get_records_by_region_default_column_name(self):
        expected_result = pd.DataFrame({'Global #': [2, 2, 1]}, index=['A', 'B', 'C'])
        result = get_records_by_region(self.df)
        pd.testing.assert_frame_equal(result, expected_result)

    def test_get_records_by_region_custom_column_name(self):
        expected_result = pd.DataFrame({'Custom Name': [2, 2, 1]}, index=['A', 'B', 'C'])
        result = get_records_by_region(self.df, column_name_to_results_global='Custom Name')
        pd.testing.assert_frame_equal(result, expected_result)

    def test_get_records_by_region_custom_region_column(self):
        expected_result = pd.DataFrame({'Global #': [2, 1]}, index=['A', 'C'])
        result = get_records_by_region(self.df, region_column_name='region', column_name_to_results_global='Global #')
        pd.testing.assert_frame_equal(result, expected_result)