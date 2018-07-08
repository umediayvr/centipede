import unittest
import os
from ..BaseTestCase import BaseTestCase
from centipede.TemplateProcedure import TemplateProcedure
from centipede.TemplateProcedure import TemplateProcedureNotFoundError

class PathTest(BaseTestCase):
    """Test Path template procedures."""

    __path = "/test/path/example.ext"
    __testRFindPath = os.path.join(BaseTestCase.dataDirectory(), 'config', 'test.json')

    def testDirname(self):
        """
        Test that the dirname procedure works properly.
        """
        result = TemplateProcedure.run("dirname", self.__path)
        self.assertEqual(result, "/test/path")

    def testParentDirname(self):
        """
        Test that the parentdirname procedure works properly.
        """
        result = TemplateProcedure.run("parentdirname", self.__path)
        self.assertEqual(result, "/test")

    def testBasename(self):
        """
        Test that the basename procedure works properly.
        """
        result = TemplateProcedure.run("basename", self.__path)
        self.assertEqual(result, "example.ext")

    def testRFindPath(self):
        """
        Test that the rfind procedure works properly.
        """
        result = TemplateProcedure.run('rfindpath', 'test.txt', self.__testRFindPath)
        testPath = os.path.join(BaseTestCase.dataDirectory(), 'test.txt')
        self.assertEqual(result, testPath)

    def testFindPath(self):
        """
        Test that the find procedure works properly.
        """
        result = TemplateProcedure.run("findpath", 'TestCrawler.py', BaseTestCase.dataDirectory())
        testPath = os.path.join(BaseTestCase.dataDirectory(), 'config', 'crawlers', 'TestCrawler.py')
        self.assertEqual(result, testPath)

    def testRegistration(self):
        """
        Test that the procedure registration works properly.
        """
        def myDummyTemplateProcedure(a, b):
            return '{}-{}'.format(a, b)

        self.assertRaises(TemplateProcedureNotFoundError, TemplateProcedure.run, "dummy")
        TemplateProcedure.register("dummy", myDummyTemplateProcedure)
        self.assertIn("dummy", TemplateProcedure.registeredNames())

    def testParseRun(self):
        """
        Test that running a procedure through string parsing works.
        """
        result = TemplateProcedure.parseRun("dirname {}".format(self.__path))
        self.assertEqual(result, "/test/path")
        self.assertRaises(AssertionError, TemplateProcedure.parseRun, True)


if __name__ == "__main__":
    unittest.main()
