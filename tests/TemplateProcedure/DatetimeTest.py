import unittest
from ..BaseTestCase import BaseTestCase
from centipede.TemplateProcedure import TemplateProcedure

class DatetimeTest(BaseTestCase):
    """Test Datetime template procedures."""

    def testYear(self):
        """
        Test that the year template procedures work properly.
        """
        yyyy = TemplateProcedure.run("yyyy")
        self.assertGreaterEqual(int(yyyy), 2018)
        yy = TemplateProcedure.run("yy")
        self.assertEqual(yyyy[-2:], yy)

    def testMonth(self):
        """
        Test that the month procedure works properly.
        """
        mm = TemplateProcedure.run("mm")
        self.assertGreaterEqual(int(mm), 1)
        self.assertLessEqual(int(mm), 12)

    def testDay(self):
        """
        Test that the day procedure works properly.
        """
        dd = TemplateProcedure.run("dd")
        self.assertGreaterEqual(int(dd), 1)
        self.assertLessEqual(int(dd), 31)

    def testHour(self):
        """
        Test that the hour procedure works properly.
        """
        hour = TemplateProcedure.run("hour")
        self.assertGreaterEqual(int(hour), 0)
        self.assertLessEqual(int(hour), 23)

    def testMinute(self):
        """
        Test that the minute procedure works properly.
        """
        minute = TemplateProcedure.run("minute")
        self.assertGreaterEqual(int(minute), 0)
        self.assertLessEqual(int(minute), 59)

    def testSecond(self):
        """
        Test that the second procedure works properly.
        """
        second = TemplateProcedure.run("second")
        self.assertGreaterEqual(int(second), 0)
        self.assertLessEqual(int(second), 59)


if __name__ == "__main__":
    unittest.main()
