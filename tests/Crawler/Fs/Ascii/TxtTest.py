import os
import unittest
from ....BaseTestCase import BaseTestCase
from ingestor.Crawler.Fs import Path
from ingestor.PathHolder import PathHolder
from ingestor.Crawler.Fs.Ascii import Txt

class TxtTest(BaseTestCase):
    """Test Txt crawler."""

    __txtFile = os.path.join(BaseTestCase.dataDirectory(), "test.txt")

    def testTxtCrawler(self):
        """
        Test that the Txt crawler test works properly.
        """
        crawler = Path.create(PathHolder(self.__txtFile))
        self.assertIsInstance(crawler, Txt)
        self.assertEqual(crawler.var("type"), "txt")
        self.assertEqual(crawler.var("category"), "ascii")

    def testContents(self):
        """
        Test that txt files are parsed properly.
        """
        crawler = Path.create(PathHolder(self.__txtFile))
        testData = "testing txt file\nwith random data\n\n1 2 3\n"
        self.assertEqual(crawler.contents(), testData)


if __name__ == "__main__":
    unittest.main()
