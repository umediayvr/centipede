import os
import unittest
from ....BaseTestCase import BaseTestCase
from ingestor.Crawler.Fs import Path
from ingestor.PathHolder import PathHolder
from ingestor.Crawler.Fs.Image import Jpg

class JpgTest(BaseTestCase):
    """Test Jpg crawler."""

    __jpgFile = os.path.join(BaseTestCase.dataDirectory(), "test.jpg")

    def testJpgCrawler(self):
        """
        Test that the Jpg crawler test works properly.
        """
        crawler = Path.create(PathHolder(self.__jpgFile))
        self.assertIsInstance(crawler, Jpg)

    def testJpgVariables(self):
        """
        Test that variables are set properly.
        """
        crawler = Path.create(PathHolder(self.__jpgFile))
        self.assertEqual(crawler.var("type"), "jpg")
        self.assertEqual(crawler.var("category"), "image")
        self.assertEqual(crawler.var("imageType"), "single")
        self.assertEqual(crawler.var("width"), 512)
        self.assertEqual(crawler.var("height"), 512)


if __name__ == "__main__":
    unittest.main()
