import unittest
from ..BaseTestCase import BaseTestCase
from centipede.ExpressionEvaluator import ExpressionEvaluator

class MathTest(BaseTestCase):
    """Test Math expressions."""

    def testSum(self):
        """
        Test that the sum expression works properly.
        """
        result = ExpressionEvaluator.run("sum", 1, 2)
        self.assertEqual(result, "3")

    def testSub(self):
        """
        Test that the sub expression works properly.
        """
        result = ExpressionEvaluator.run("sub", 1, 2)
        self.assertEqual(result, "-1")

    def testMult(self):
        """
        Test that the mult expression works properly.
        """
        result = ExpressionEvaluator.run("mult", 2, 3)
        self.assertEqual(result, "6")

    def testDiv(self):
        """
        Test that the div expression works properly.
        """
        result = ExpressionEvaluator.run("div", 6, 2)
        self.assertEqual(result, "3")

    def testMin(self):
        """
        Test that the min expression works properly.
        """
        result = ExpressionEvaluator.run("min", 6, 2)
        self.assertEqual(result, "2")

    def testMax(self):
        """
        Test that the max expression works properly.
        """
        result = ExpressionEvaluator.run("max", 6, 2)
        self.assertEqual(result, "6")

if __name__ == "__main__":
    unittest.main()
