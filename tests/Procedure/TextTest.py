import unittest
from ..BaseTestCase import BaseTestCase
from centipede.Procedure import Procedure

class TextTest(BaseTestCase):
    """Test Text procedures."""

    def testUpper(self):
        """
        Test that the upper procedure works properly.
        """
        result = Procedure.run("upper", "boop")
        self.assertEqual(result, "BOOP")

    def testLower(self):
        """
        Test that the lower procedure works properly.
        """
        result = Procedure.run("lower", "BOOP")
        self.assertEqual(result, "boop")

    def testReplace(self):
        """
        Test that the replace procedure works properly.
        """
        result = Procedure.run("replace", "Boop", "o", "e")
        self.assertEqual(result, "Beep")

    def testRemove(self):
        """
        Test that the remove procedure works properly.
        """
        result = Procedure.run("remove", "boop", "p")
        self.assertEqual(result, "boo")


if __name__ == "__main__":
    unittest.main()
