import os
import unittest
from ....BaseTestCase import BaseTestCase
from centipede.Crawler import Crawler
from centipede.PathHolder import PathHolder
from centipede.Crawler.Fs.Video import Mov

class MovTest(BaseTestCase):
    """Test Texture crawler."""

    __movFile = os.path.join(BaseTestCase.dataDirectory(), "test.mov")
    __movNoTimecodeFile = os.path.join(BaseTestCase.dataDirectory(), "testNoTimecode.mov")

    def testMovCrawler(self):
        """
        Test that the Mov crawler test works properly.
        """
        crawler = Crawler.create(PathHolder(self.__movFile))
        self.assertIsInstance(crawler, Mov)

    def testMovVariables(self):
        """
        Test that variables are set properly.
        """
        crawler = Crawler.create(PathHolder(self.__movFile))
        self.assertEqual(crawler.var("type"), "mov")
        self.assertEqual(crawler.var("category"), "video")
        self.assertEqual(crawler.var("width"), 1920)
        self.assertEqual(crawler.var("height"), 1080)
        self.assertEqual(crawler.var("firstFrame"), 1)
        self.assertEqual(crawler.var("lastFrame"), 12)

        crawler = Crawler.create(PathHolder(self.__movNoTimecodeFile))
        self.assertFalse("firstFrame" in crawler.varNames())
        self.assertFalse("lastFrame" in crawler.varNames())

    def testMovTags(self):
        """
        Test that the tags are set properly.
        """
        crawler = Crawler.create(PathHolder(self.__movFile))
        self.assertEqual(crawler.tag("video"), "test.mov")


if __name__ == "__main__":
    unittest.main()
