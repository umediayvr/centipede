import unittest
from ..BaseTestCase import BaseTestCase
from centipede.ExpressionEvaluator import ExpressionEvaluator

class DatetimeTest(BaseTestCase):
    """Test Datetime expressions."""

    def testYear(self):
        """
        Test that the year expressions work properly.
        """
        yyyy = ExpressionEvaluator.run("yyyy")
        self.assertGreaterEqual(int(yyyy), 2018)
        yy = ExpressionEvaluator.run("yy")
        self.assertEqual(yyyy[-2:], yy)

    def testMonth(self):
        """
        Test that the month expression works properly.
        """
        mm = ExpressionEvaluator.run("mm")
        self.assertGreaterEqual(int(mm), 1)
        self.assertLessEqual(int(mm), 12)

    def testDay(self):
        """
        Test that the day expression works properly.
        """
        dd = ExpressionEvaluator.run("dd")
        self.assertGreaterEqual(int(dd), 1)
        self.assertLessEqual(int(dd), 31)

    def testHour(self):
        """
        Test that the hour expression works properly.
        """
        hour = ExpressionEvaluator.run("hour")
        self.assertGreaterEqual(int(hour), 0)
        self.assertLessEqual(int(hour), 23)

    def testMinute(self):
        """
        Test that the minute expression works properly.
        """
        minute = ExpressionEvaluator.run("minute")
        self.assertGreaterEqual(int(minute), 0)
        self.assertLessEqual(int(minute), 59)

    def testSecond(self):
        """
        Test that the second expression works properly.
        """
        second = ExpressionEvaluator.run("second")
        self.assertGreaterEqual(int(second), 0)
        self.assertLessEqual(int(second), 59)


if __name__ == "__main__":
    unittest.main()
