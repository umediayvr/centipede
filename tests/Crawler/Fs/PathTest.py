import os
import glob
import unittest
from ...BaseTestCase import BaseTestCase
from ingestor.Crawler.Fs import Path
from ingestor.PathHolder import PathHolder
from ingestor.Crawler.Fs.Render import ExrRender

class PathTest(BaseTestCase):
    """Test Directory crawler."""

    __dir = os.path.join(BaseTestCase.dataDirectory(), "glob")
    __turntableFile = os.path.join(__dir, "images", "RND_ass_lookdev_default_beauty_tt.1001.exr")

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

        crawlers = crawler.glob(filterTypes=["turntable"])
        crawlerPaths = list(map(lambda x: x.var("filePath"), crawlers))
        self.assertEqual(crawlerPaths, [self.__turntableFile])

        crawlers = crawler.glob(filterTypes=[ExrRender])
        crawlerPaths = list(map(lambda x: x.var("filePath"), crawlers))
        result = glob.glob("{}/**/RND**.exr".format(self.__dir), recursive=True)
        result = list(map(lambda x: x.rstrip("/"), result))
        self.assertCountEqual(result, crawlerPaths)

        crawler = Path.create(PathHolder(self.__turntableFile))
        otherCrawlers = crawler.globFromParent(filterTypes=[ExrRender])
        crawlerPaths = list(map(lambda x: x.var("filePath"), crawlers))
        otherCrawlerPaths = list(map(lambda x: x.var("filePath"), otherCrawlers))
        self.assertCountEqual(crawlerPaths, otherCrawlerPaths)

    def testCrawlerRegistration(self):
        """
        Test that you can register a new Path crawler.
        """
        class DummyCrawler(Path):
            @classmethod
            def test(cls, pathHolder, parentCrawler):
                return False

        Path.register("dummy", DummyCrawler)
        self.assertIn("dummy", Path.registeredNames())


if __name__ == "__main__":
    unittest.main()
