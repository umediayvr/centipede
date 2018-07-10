import unittest
from ..BaseTestCase import BaseTestCase
from centipede.TemplateProcedure import TemplateProcedure

class MathTest(BaseTestCase):
    """Test Math template procedures."""

    def testSum(self):
        """
        Test that the sum procedure works properly.
        """
        result = TemplateProcedure.run("sum", 1, 2)
        self.assertEqual(result, "3")

    def testSub(self):
        """
        Test that the sub procedure works properly.
        """
        result = TemplateProcedure.run("sub", 1, 2)
        self.assertEqual(result, "-1")

    def testMult(self):
        """
        Test that the mult procedure works properly.
        """
        result = TemplateProcedure.run("mult", 2, 3)
        self.assertEqual(result, "6")

    def testDiv(self):
        """
        Test that the div procedure works properly.
        """
        result = TemplateProcedure.run("div", 6, 2)
        self.assertEqual(result, "3")

    def testMin(self):
        """
        Test that the min procedure works properly.
        """
        result = TemplateProcedure.run("min", 6, 2)
        self.assertEqual(result, "2")

    def testMax(self):
        """
        Test that the max procedure works properly.
        """
        result = TemplateProcedure.run("max", 6, 2)
        self.assertEqual(result, "6")

if __name__ == "__main__":
    unittest.main()
