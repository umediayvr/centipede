import os
import unittest
from ....BaseTestCase import BaseTestCase
from ingestor.Crawler.Fs import Path
from ingestor.PathHolder import PathHolder
from ingestor.Crawler.Fs.Scene import MayaScene
from ingestor.Crawler.Fs.Scene import Scene


class MayaSceneTest(BaseTestCase):
    """Test Maya Scene crawler."""

    __maFile = os.path.join(BaseTestCase.dataDirectory(), "test.ma")
    __mbFile = os.path.join(BaseTestCase.dataDirectory(), "test.mb")

    def testMayaSceneCrawler(self):
        """
        Test that the Maya Scene crawler test works properly.
        """
        crawler = Path.create(PathHolder(self.__maFile))
        self.assertIsInstance(crawler, MayaScene)
        crawler = Path.create(PathHolder(self.__mbFile))
        self.assertIsInstance(crawler, MayaScene)

    def testMayaSceneVariables(self):
        """
        Test that variables are set properly.
        """
        crawler = Path.create(PathHolder(self.__maFile))
        self.assertEqual(crawler.var("type"), "mayaScene")
        self.assertEqual(crawler.var("category"), "scene")

    def testMayaSceneExtensions(self):
        """
        Test that the list of extensions matching maya scenes is correct.
        """
        self.assertCountEqual(MayaScene.extensions(), ["ma", "mb"])
        self.assertRaises(NotImplementedError, Scene.extensions)


if __name__ == "__main__":
    unittest.main()
