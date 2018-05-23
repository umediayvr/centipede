import os
import unittest
from ....BaseTestCase import BaseTestCase
from ingestor.Crawler import Crawler
from ingestor.PathHolder import PathHolder
from ingestor.Crawler.Fs.Lut import Ccc

class CccTest(BaseTestCase):
    """Test Ccc crawler."""

    __cccFile = os.path.join(BaseTestCase.dataDirectory(), "test.ccc")

    def testCccCrawler(self):
        """
        Test that the Ccc crawler test works properly.
        """
        crawler = Crawler.create(PathHolder(self.__cccFile))
        self.assertIsInstance(crawler, Ccc)

    def testCccVariables(self):
        """
        Test that variables are set properly.
        """
        crawler = Crawler.create(PathHolder(self.__cccFile))
        self.assertEqual(crawler.var("type"), "ccc")
        self.assertEqual(crawler.var("category"), "lut")
        self.assertEqual(crawler.var("slope"), [1.1, 1.2, 1.3])
        self.assertEqual(crawler.var("offset"), [0.1, 0.2, 0.3])
        self.assertEqual(crawler.var("power"), [1.4, 1.5, 1.6])
        self.assertEqual(crawler.var("saturation"), 1.0)


if __name__ == "__main__":
    unittest.main()
