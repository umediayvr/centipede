import unittest
from ..BaseTestCase import BaseTestCase
from ingestor.ExpressionEvaluator import ExpressionEvaluator

class PathTest(BaseTestCase):
    """Test Path expressions."""

    __path = "/test/path/example.ext"

    def testDirname(self):
        """
        Test that the dirname expression works properly.
        """
        result = ExpressionEvaluator.run("dirname", self.__path)
        self.assertEqual(result, "/test/path")

    def testParentDirname(self):
        """
        Test that the parentdirname expression works properly.
        """
        result = ExpressionEvaluator.run("parentdirname", self.__path)
        self.assertEqual(result, "/test")

    def testBasename(self):
        """
        Test that the basename expression works properly.
        """
        result = ExpressionEvaluator.run("basename", self.__path)
        self.assertEqual(result, "example.ext")


if __name__ == "__main__":
    unittest.main()
