import unittest
from ..BaseTestCase import BaseTestCase
from centipede.ExpressionEvaluator import ExpressionEvaluator

class TextTest(BaseTestCase):
    """Test Text expressions."""

    def testUpper(self):
        """
        Test that the upper expression works properly.
        """
        result = ExpressionEvaluator.run("upper", "boop")
        self.assertEqual(result, "BOOP")

    def testLower(self):
        """
        Test that the lower expression works properly.
        """
        result = ExpressionEvaluator.run("lower", "BOOP")
        self.assertEqual(result, "boop")

    def testReplace(self):
        """
        Test that the replace expression works properly.
        """
        result = ExpressionEvaluator.run("replace", "Boop", "o", "e")
        self.assertEqual(result, "Beep")

    def testRemove(self):
        """
        Test that the remove expression works properly.
        """
        result = ExpressionEvaluator.run("remove", "boop", "p")
        self.assertEqual(result, "boo")


if __name__ == "__main__":
    unittest.main()
