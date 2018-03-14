import os
import unittest
from ....BaseTestCase import BaseTestCase
from ingestor.Crawler.Fs import Path
from ingestor.PathHolder import PathHolder
from ingestor.Crawler.Fs.Video import Mov

class MovTest(BaseTestCase):
    """Test Texture crawler."""

    __movFile = os.path.join(BaseTestCase.dataDirectory(), "test.mov")

    def testMovCrawler(self):
        """
        Test that the Mov crawler test works properly.
        """
        crawler = Path.create(PathHolder(self.__movFile))
        self.assertIsInstance(crawler, Mov)

    def testMovVariables(self):
        """
        Test that variables are set properly.
        """
        crawler = Path.create(PathHolder(self.__movFile))
        self.assertEqual(crawler.var("type"), "mov")
        self.assertEqual(crawler.var("category"), "video")
        self.assertEqual(crawler.var("width"), 1920)
        self.assertEqual(crawler.var("height"), 1080)
        self.assertEqual(crawler.var("firstFrame"), 1)
        self.assertEqual(crawler.var("lastFrame"), 12)

    def testMovTags(self):
        """
        Test that the tags are set properly.
        """
        crawler = Path.create(PathHolder(self.__movFile))
        self.assertEqual(crawler.tag("video"), "test.mov")


if __name__ == "__main__":
    unittest.main()
