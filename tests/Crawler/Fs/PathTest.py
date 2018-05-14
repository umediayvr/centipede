import os
import glob
import unittest
from ...BaseTestCase import BaseTestCase
from centipede.Crawler.Fs import Path
from centipede.Crawler.Fs import File
from centipede.PathHolder import PathHolder
from centipede.Crawler.Fs.Render import ExrRender
from centipede.Crawler.Fs.Image import Exr
from centipede.Crawler.Crawler import InvalidVarError
from centipede.Crawler.Crawler import InvalidTagError

class PathTest(BaseTestCase):
    """Test Directory crawler."""

    __dir = os.path.join(BaseTestCase.dataDirectory(), "glob")
    __turntableFile = os.path.join(__dir, "images", "RND_ass_lookdev_default_beauty_tt.1001.exr")
    __shotRenderFile = os.path.join(__dir, "images", "RND-TST-SHT_lighting_beauty_sr.1001.exr")

    def testPathCrawler(self):
        """
        Test that the Path crawler test is not implemented.
        """
        pathHolder = PathHolder(self.__dir)
        self.assertRaises(NotImplementedError, Path.test, pathHolder, None)

    def testPathGlob(self):
        """
        Test the glob functionality.
        """
        crawler = Path.create(PathHolder(self.__dir))
        crawlers = crawler.glob()
        result = glob.glob("{}/**".format(self.__dir), recursive=True)
        result = list(map(lambda x: x.rstrip("/"), result))
        crawlerPaths = list(map(lambda x: x.var("filePath"), crawlers))
        self.assertCountEqual(result, crawlerPaths)

        crawlers = crawler.glob(filterTypes=["turntable", "shotRender"])
        crawlerPaths = list(map(lambda x: x.var("filePath"), crawlers))
        self.assertCountEqual(crawlerPaths, [self.__turntableFile, self.__shotRenderFile])

        crawlers = crawler.glob(filterTypes=[ExrRender])
        crawlerPaths = list(map(lambda x: x.var("filePath"), crawlers))
        result = glob.glob("{}/**/RND**.exr".format(self.__dir), recursive=True)
        result = list(map(lambda x: x.rstrip("/"), result))
        self.assertCountEqual(result, crawlerPaths)

        crawlers = crawler.glob(filterTypes=['exr'])
        crawlerPaths = list(map(lambda x: x.var("filePath"), crawlers))
        result = glob.glob("{}/**/**.exr".format(self.__dir), recursive=True)
        result = list(map(lambda x: x.rstrip("/"), result))
        self.assertCountEqual(result, crawlerPaths)

        crawler = Path.create(PathHolder(self.__turntableFile))
        otherCrawlers = crawler.globFromParent(filterTypes=[ExrRender])
        crawlerPaths = list(map(lambda x: x.var("filePath"), crawlers))
        otherCrawlerPaths = list(map(lambda x: x.var("filePath"), otherCrawlers))
        self.assertCountEqual(crawlerPaths, otherCrawlerPaths)

    def testPathVariables(self):
        """
        Test that the Path Crawler variables are set properly.
        """
        crawler = Path.create(PathHolder(self.__turntableFile))
        name, ext = os.path.splitext(self.__turntableFile)
        self.assertEqual(crawler.var('filePath'), self.__turntableFile)
        self.assertEqual(crawler.var('ext'), ext.lstrip("."))
        self.assertEqual(crawler.var('baseName'), os.path.basename(self.__turntableFile))
        self.assertEqual(crawler.var('name'), os.path.basename(name).split(".")[0])
        self.assertEqual(crawler.var('sourceDirectory'), os.path.dirname(name))
        self.assertRaises(InvalidVarError, crawler.var, "dummyVar")

    def testPathTags(self):
        """
        Test that the Path Crawler tags are set properly.
        """
        crawler = Path.create(PathHolder(self.__turntableFile))
        self.assertRaises(InvalidTagError, crawler.tag, "dummyTag")

    def testCrawlerRegistration(self):
        """
        Test that you can register a new Path crawler.
        """
        class DummyCrawler(File):
            @classmethod
            def test(cls, pathHolder, parentCrawler):
                return False

        Path.register("dummy", DummyCrawler)
        self.assertIn("dummy", Path.registeredNames())
        self.assertIn(DummyCrawler, Path.registeredSubclasses("generic"))
        self.assertIn(DummyCrawler, Path.registeredSubclasses(Path))

    def testPathClone(self):
        """
        Test that cloning crawlers works.
        """
        crawler = Path.create(PathHolder(self.__turntableFile))
        clone = crawler.clone()
        self.assertCountEqual(crawler.varNames(), clone.varNames())
        self.assertCountEqual(crawler.contextVarNames(), clone.contextVarNames())
        self.assertCountEqual(crawler.tagNames(), clone.tagNames())
        self.assertRaises(NotImplementedError, super(Path, crawler).clone)

    def testPathJson(self):
        """
        Test that you can convert a Path crawler to json and back.
        """
        crawler = Path.create(PathHolder(self.__turntableFile))
        jsonResult = crawler.toJson()
        crawlerResult = Path.createFromJson(jsonResult)
        self.assertCountEqual(crawler.varNames(), crawlerResult.varNames())
        self.assertCountEqual(crawler.contextVarNames(), crawlerResult.contextVarNames())
        self.assertCountEqual(crawler.tagNames(), crawlerResult.tagNames())

    def testPathCreate(self):
        """
        Test that you can create a crawler with a specific type.
        """
        crawler = Path.createFromPath(self.__turntableFile, "exr")
        self.assertIsInstance(crawler, Exr)

    def testPathHolder(self):
        """
        Test PathHolder functions.
        """
        pathHolder = PathHolder(self.__turntableFile)
        self.assertEqual(pathHolder.size(), 5430903)
        self.assertEqual(pathHolder.name(), "RND_ass_lookdev_default_beauty_tt.1001")
        self.assertTrue(pathHolder.exists())
        pathHolder = PathHolder("/")
        self.assertEqual(pathHolder.baseName(), os.sep)


if __name__ == "__main__":
    unittest.main()
