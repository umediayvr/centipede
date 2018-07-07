import unittest
from ..BaseTestCase import BaseTestCase
from centipede.Procedure import Procedure

class MathTest(BaseTestCase):
    """Test Math procedures."""

    def testSum(self):
        """
        Test that the sum procedure works properly.
        """
        result = Procedure.run("sum", 1, 2)
        self.assertEqual(result, "3")

    def testSub(self):
        """
        Test that the sub procedure works properly.
        """
        result = Procedure.run("sub", 1, 2)
        self.assertEqual(result, "-1")

    def testMult(self):
        """
        Test that the mult procedure works properly.
        """
        result = Procedure.run("mult", 2, 3)
        self.assertEqual(result, "6")

    def testDiv(self):
        """
        Test that the div procedure works properly.
        """
        result = Procedure.run("div", 6, 2)
        self.assertEqual(result, "3")

    def testMin(self):
        """
        Test that the min procedure works properly.
        """
        result = Procedure.run("min", 6, 2)
        self.assertEqual(result, "2")

    def testMax(self):
        """
        Test that the max procedure works properly.
        """
        result = Procedure.run("max", 6, 2)
        self.assertEqual(result, "6")

if __name__ == "__main__":
    unittest.main()
