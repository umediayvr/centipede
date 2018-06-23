import unittest
import os
from ..BaseTestCase import BaseTestCase
from ingestor.Task import Task
from ingestor.TaskWrapper import TaskWrapper
from ingestor.Crawler.Fs import FsPath
from ingestor.Resource import Resource

class UPython2Test(BaseTestCase):
    """Test UPython2Test subprocess."""

    __sourcePath = os.path.join(BaseTestCase.dataDirectory(), "test.exr")
    __taskPath = os.path.join(BaseTestCase.dataDirectory(), "tasks", "UPythonMajorVerTestTask.py")

    def testUpython2(self):
        """
        Test that the upython3 subprocess works properly.
        """
        resource = Resource.get()
        resource.load(self.__taskPath)
        pathCrawler = FsPath.createFromPath(self.__sourcePath)
        dummyTask = Task.create('uPythonMajorVerTestTask')
        dummyTask.add(pathCrawler)

        wrapper = TaskWrapper.create("upython2")
        result = wrapper.run(dummyTask)
        self.assertTrue(len(result), 1)
        self.assertEqual(result[0].var("majorVer"), 2)


if __name__ == "__main__":
    unittest.main()
