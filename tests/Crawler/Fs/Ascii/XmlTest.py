import os
import unittest
from ....BaseTestCase import BaseTestCase
from ingestor.Crawler.Fs import Path
from ingestor.Crawler.Fs.Ascii import Xml

class XmlTest(BaseTestCase):
    """Test Xml crawler."""

    __xmlFile = os.path.join(BaseTestCase.dataDirectory(), "test.xml")

    def testXmlCrawler(self):
        """
        Test that the Xml crawler test works properly.
        """
        crawler = Path.createFromPath(self.__xmlFile)
        self.assertIsInstance(crawler, Xml)

    def testXmlVariables(self):
        """
        Test that variables are set properly.
        """
        crawler = Path.createFromPath(self.__xmlFile)
        self.assertEqual(crawler.var("type"), "xml")
        self.assertEqual(crawler.var("category"), "ascii")

    def testXmlContents(self):
        """
        Test that txt files are parsed properly.
        """
        crawler = Path.createFromPath(self.__xmlFile)
        self.assertEqual(crawler.queryTag('testC'), "testing child C")
        self.assertEqual(crawler.queryTag('testD1'), "1 2 3")
        self.assertEqual(crawler.queryTag('{TestNamespace}testD1', ignoreNameSpace=False), "1 2 3")


if __name__ == "__main__":
    unittest.main()
