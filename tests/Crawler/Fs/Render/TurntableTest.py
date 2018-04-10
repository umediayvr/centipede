import os
import unittest
from ....BaseTestCase import BaseTestCase
from ingestor.Crawler.Fs import Path
from ingestor.PathHolder import PathHolder
from ingestor.Crawler.Fs.Render import Turntable

class TurntableTest(BaseTestCase):
    """Test Turntable crawler."""

    __exrFile = os.path.join(BaseTestCase.dataDirectory(), "RND_ass_lookdev_default_beauty_tt.1001.exr")

    def testTurntableCrawler(self):
        """
        Test that the Turntable crawler test works properly.
        """
        crawler = Path.create(PathHolder(self.__exrFile))
        self.assertIsInstance(crawler, Turntable)

    def testTurntableVariables(self):
        """
        Test that variables are set properly.
        """
        crawler = Path.create(PathHolder(self.__exrFile))
        self.assertEqual(crawler.var("type"), "turntable")
        self.assertEqual(crawler.var("category"), "render")
        self.assertEqual(crawler.var("renderType"), "tt")
        self.assertEqual(crawler.var("assetName"), "ass")
        self.assertEqual(crawler.var("step"), "lookdev")
        self.assertEqual(crawler.var("pass"), "beauty")
        self.assertEqual(crawler.var("renderName"), "ass-default-beauty")


if __name__ == "__main__":
    unittest.main()
