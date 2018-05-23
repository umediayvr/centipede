import unittest
import os
from ...BaseTestCase import BaseTestCase
from ingestor.Task import Task
from ingestor.Crawler.Fs import FsPath

class ConvertImageTest(BaseTestCase):
    """
    Test ConvertImage task.

    Note that the convert image task will add time metadata on EXR and TIF files so they wouldn't pass the
    checksum test here.
    """

    __sourcePath = os.path.join(BaseTestCase.dataDirectory(), "test.exr")
    __testPath = os.path.join(BaseTestCase.dataDirectory(), "convertImage.jpg")
    __targetPath = os.path.join(BaseTestCase.dataDirectory(), "testToDelete.jpg")

    def testConvertImage(self):
        """
        Test that the ConvertImage task works properly.
        """
        pathCrawler = FsPath.createFromPath(self.__sourcePath)
        convertTask = Task.create('convertImage')
        convertTask.add(pathCrawler, self.__targetPath)
        result = convertTask.output()
        convertTask = Task.create('convertImage')
        convertTask.add(pathCrawler, self.__testPath)
        result = convertTask.output()
        self.assertEqual(len(result), 1)
        checkTask = Task.create('checksum')
        checkTask.add(result[0], self.__testPath)
        checkTask.output()

    @classmethod
    def tearDownClass(cls):
        """
        Remove the file that was copied.
        """
        os.remove(cls.__targetPath)


if __name__ == "__main__":
    unittest.main()
