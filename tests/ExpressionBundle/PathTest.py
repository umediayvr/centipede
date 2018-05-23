import unittest
import os
from ..BaseTestCase import BaseTestCase
from ingestor.ExpressionEvaluator import ExpressionEvaluator
from ingestor.ExpressionEvaluator import ExpressionNotFoundError

class PathTest(BaseTestCase):
    """Test Path expressions."""

    __path = "/test/path/example.ext"
    __testRFindPath = os.path.join(BaseTestCase.dataDirectory(), 'config', 'test.json')

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

    def testRFindPath(self):
        """
        Test that the rfind expression works properly.
        """
        result = ExpressionEvaluator.run('rfindpath', 'test.txt', self.__testRFindPath)
        testPath = os.path.join(BaseTestCase.dataDirectory(), 'test.txt')
        self.assertEqual(result, testPath)

    def testFindPath(self):
        """
        Test that the find expression works properly.
        """
        result = ExpressionEvaluator.run("findpath", 'TestCrawler.py', BaseTestCase.dataDirectory())
        testPath = os.path.join(BaseTestCase.dataDirectory(), 'config', 'crawlers', 'TestCrawler.py')
        self.assertEqual(result, testPath)

    def testRegistration(self):
        """
        Test that the expression registration works properly.
        """
        self.assertRaises(ExpressionNotFoundError, ExpressionEvaluator.run, "dummy")
        ExpressionEvaluator.register("dummy", print)
        self.assertIn("dummy", ExpressionEvaluator.registeredNames())

    def testParseRun(self):
        """
        Test that running an expression through string parsing works.
        """
        result = ExpressionEvaluator.parseRun("dirname {}".format(self.__path))
        self.assertEqual(result, "/test/path")
        self.assertRaises(AssertionError, ExpressionEvaluator.parseRun, True)


if __name__ == "__main__":
    unittest.main()
