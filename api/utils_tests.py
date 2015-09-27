# Inspired by https://cloud.google.com/appengine/docs/python/tools/localunittesting

# Correct path so ndb can be imported (in models.py)
import sys
sys.path.insert(0, "C:\Program Files (x86)\Google\google_appengine")
import dev_appserver
dev_appserver.fix_sys_path()

import unittest
import utils


class TestUtilsFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_is_now_in_start_end_time_range_adjusted_for_timezone_offset_issue(self):
        # Underflow
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(-2, 2, 21))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(-2, 2, 22))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(-2, 2, 23))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(-2, 2, 24))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(-2, 2, 0))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(-2, 2, 1))
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(-2, 2, 2))

        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(-2, 22, 2))

        # Overflow
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(21, 26, 20))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(21, 26, 21))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(21, 26, 22))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(21, 26, 23))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(21, 26, 24))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(21, 26, 0))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(21, 26, 1))
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(21, 26, 2))

        # Normal
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(11, 15, 9))
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(11, 15, 10))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(11, 15, 11))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(11, 15, 12))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(11, 15, 13))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(11, 15, 14))
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(11, 15, 15))
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(11, 15, 16))

        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(0, 24, 0))

        # Normal - edge case 0
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(0, 1, 23))
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(0, 1, 24))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(0, 1, 0))
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(0, 1, 1))
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(0, 1, 2))

        # Normal - edge case 24
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(23, 24, 22))
        self.assertTrue(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(23, 24, 23))
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(23, 24, 24))
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(23, 24, 0))
        self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(23, 24, 1))

        # Equal, this is the same as disabled
        for hour in range(25):
            self.assertFalse(utils.is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(hour, hour, hour))


if __name__ == '__main__':
    unittest.main()