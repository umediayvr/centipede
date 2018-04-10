import os
import unittest
from ....BaseTestCase import BaseTestCase
from ingestor.Crawler.Fs import Path
from ingestor.PathHolder import PathHolder
from ingestor.Crawler.Fs.Image import Dpx

class DpxTest(BaseTestCase):
    """Test Dpx crawler."""

    __dpxFile = os.path.join(BaseTestCase.dataDirectory(), "test.dpx")

    def testDpxCrawler(self):
        """
        Test that the Dpx crawler test works properly.
        """
        crawler = Path.create(PathHolder(self.__dpxFile))
        self.assertIsInstance(crawler, Dpx)

    def testDpxVariables(self):
        """
        Test that variables are set properly.
        """
        crawler = Path.create(PathHolder(self.__dpxFile))
        self.assertEqual(crawler.var("type"), "dpx")
        self.assertEqual(crawler.var("category"), "image")
        self.assertEqual(crawler.var("imageType"), "single")
        self.assertEqual(crawler.var("width"), 2048)
        self.assertEqual(crawler.var("height"), 1080)


if __name__ == "__main__":
    unittest.main()
