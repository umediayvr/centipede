import unittest
import os
from ...BaseTestCase import BaseTestCase
from ingestor.Task import Task
from ingestor.Crawler.Fs import Path

class ResizeImageTest(BaseTestCase):
    """Test ResizeImage task."""

    __sourcePath = os.path.join(BaseTestCase.dataDirectory(), "test.0001.exr")
    __testPath = os.path.join(BaseTestCase.dataDirectory(), "resizeImage.jpg")
    __targetPath = os.path.join(BaseTestCase.dataDirectory(), "testToDelete.jpg")

    def testResizeImage(self):
        """
        Test that the ResizeImage task works properly.
        """
        pathCrawler = Path.createFromPath(self.__sourcePath)
        resizeTask = Task.create('resizeImage')
        resizeTask.add(pathCrawler, self.__targetPath)
        resizeTask.setOption("width", "480")
        resizeTask.setOption("height", "270")
        for convertToRGBA in [False, True]:
            with self.subTest(convertToRGBA=convertToRGBA):
                resizeTask.setOption("convertToRGBA", convertToRGBA)
                result = resizeTask.output()
                self.assertEqual(len(result), 1)
                crawler = result[0]
                self.assertEqual(crawler.var("width"), 480)
                self.assertEqual(crawler.var("height"), 270)
                checkTask = Task.create('checksum')
                checkTask.add(crawler, self.__testPath)
                checkTask.output()

    @classmethod
    def tearDownClass(cls):
        """
        Remove the file that was copied.
        """
        os.remove(cls.__targetPath)


if __name__ == "__main__":
    unittest.main()
