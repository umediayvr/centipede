import os
import unittest
from ....BaseTestCase import BaseTestCase
from ingestor.Crawler.Fs import Path
from ingestor.PathHolder import PathHolder
from ingestor.Crawler.Fs.Texture import Texture

class TextureTest(BaseTestCase):
    """Test Texture crawler."""

    __exrFile = os.path.join(BaseTestCase.dataDirectory(), "test_DIFF_u1_v1.exr")
    __tifFile = os.path.join(BaseTestCase.dataDirectory(), "test_bump_1002.tif")
    __badExrFile = os.path.join(BaseTestCase.dataDirectory(), "test_0001.exr")

    def testTextureCrawler(self):
        """
        Test that the Texture crawler test works properly.
        """
        crawler = Path.create(PathHolder(self.__exrFile))
        self.assertIsInstance(crawler, Texture)
        crawler = Path.create(PathHolder(self.__tifFile))
        self.assertIsInstance(crawler, Texture)
        crawler = Path.create(PathHolder(self.__badExrFile))
        self.assertNotIsInstance(crawler, Texture)

    def testTextureVariables(self):
        """
        Test that variables are set properly.
        """
        crawler = Path.create(PathHolder(self.__exrFile))
        self.assertEqual(crawler.var("type"), "texture")
        self.assertEqual(crawler.var("category"), "texture")
        self.assertEqual(crawler.var("assetName"), "test")
        self.assertEqual(crawler.var("mapType"), "DIFF")
        self.assertEqual(crawler.var("udim"), 1001)
        self.assertEqual(crawler.var("variant"), "default")

        crawler = Path.create(PathHolder(self.__tifFile))
        self.assertEqual(crawler.var("assetName"), "test")
        self.assertEqual(crawler.var("mapType"), "BUMP")
        self.assertEqual(crawler.var("udim"), 1002)
        self.assertEqual(crawler.var("variant"), "default")

    def testTextureTags(self):
        """
        Test that the tags are set properly.
        """
        crawler = Path.create(PathHolder(self.__exrFile))
        self.assertEqual(crawler.tag("group"), "test-default")


if __name__ == "__main__":
    unittest.main()
