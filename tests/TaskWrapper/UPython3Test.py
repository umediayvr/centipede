import unittest
import os
from ..BaseTestCase import BaseTestCase
from centipede.Task import Task
from centipede.TaskWrapper import TaskWrapper
from centipede.Crawler.Fs import FsPath
from centipede.Resource import Resource

class UPython3Test(BaseTestCase):
    """Test UPython3Test subprocess."""

    __sourcePath = os.path.join(BaseTestCase.dataDirectory(), "test.exr")
    __taskPath = os.path.join(BaseTestCase.dataDirectory(), "tasks", "UPythonMajorVerTestTask.py")

    def testUpython3(self):
        """
        Test that the upython3 subprocess works properly.
        """
        resource = Resource.get()
        resource.load(self.__taskPath)
        pathCrawler = FsPath.createFromPath(self.__sourcePath)
        dummyTask = Task.create('uPythonMajorVerTestTask')
        dummyTask.add(pathCrawler)

        wrapper = TaskWrapper.create("upython3")
        result = wrapper.run(dummyTask)
        self.assertTrue(len(result), 1)
        self.assertEqual(result[0].var("majorVer"), 3)


if __name__ == "__main__":
    unittest.main()
