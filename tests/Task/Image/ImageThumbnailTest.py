import unittest
import os
from ...BaseTestCase import BaseTestCase
from ingestor.Task import Task
from ingestor.Crawler.Fs import FsPath

class ImageThumbnailTest(BaseTestCase):
    """Test ImageThumbnail task."""

    __sourcePath = os.path.join(BaseTestCase.dataDirectory(), "test.dpx")
    __testPath = os.path.join(BaseTestCase.dataDirectory(), "thumbnailImage.jpg")
    __targetPath = os.path.join(BaseTestCase.dataDirectory(), "testToDelete.jpg")

    def testImageThumbnail(self):
        """
        Test that the ImageThumbnail task works properly.
        """
        pathCrawler = FsPath.createFromPath(self.__sourcePath)
        thumbnailTask = Task.create('imageThumbnail')
        thumbnailTask.add(pathCrawler, self.__targetPath)
        result = thumbnailTask.output()
        self.assertEqual(len(result), 1)
        crawler = result[0]
        self.assertEqual(crawler.var("width"), 640)
        self.assertEqual(crawler.var("height"), 337)
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
