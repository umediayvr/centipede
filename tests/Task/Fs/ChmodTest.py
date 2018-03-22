import unittest
import os
from ...BaseTestCase import BaseTestCase
from ingestor.Task import Task
from ingestor.Crawler.Fs import Path

class ChmodTest(BaseTestCase):
    """Test Chmod task."""

    __dir = os.path.join(BaseTestCase.dataDirectory(), "glob")
    __path = os.path.join(__dir, "images", "RND_ass_lookdev_default_beauty_tt.1001.exr")

    def testChmodFile(self):
        """
        Test that the chmod task works properly on a file.
        """
        pathCrawler = Path.createFromPath(self.__path)
        chmodTask = Task.create('chmod')
        chmodTask.add(pathCrawler, self.__path)
        for permission in ["644", "444", "744", "664"]:
            with self.subTest(permission=permission):
                chmodTask.setOption('directoryMode', permission)
                chmodTask.setOption('fileMode', permission)
                result = chmodTask.output()
                self.assertEqual(len(result), 1)
                crawler = result[0]
                self.assertEqual(self.__getPermission(crawler.var('filePath')), permission)

    def testChmodDir(self):
        """
        Test that the chmod task works properly on a directory.
        """
        pathCrawler = Path.createFromPath(self.__dir)
        chmodTask = Task.create('chmod')
        chmodTask.add(pathCrawler, self.__dir)
        dirPerm = "775"
        filePerm = "664"
        chmodTask.setOption('directoryMode', dirPerm)
        chmodTask.setOption('fileMode', filePerm)
        result = chmodTask.output()
        self.assertEqual(len(result), 1)
        self.assertEqual(self.__getPermission(self.__dir), dirPerm)
        self.assertEqual(self.__getPermission(self.__path), filePerm)

    @staticmethod
    def __getPermission(filePath):
        return oct(os.stat(filePath).st_mode)[-3:]


if __name__ == "__main__":
    unittest.main()
