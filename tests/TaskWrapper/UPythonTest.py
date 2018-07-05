import unittest
import os
import OpenImageIO
from ..BaseTestCase import BaseTestCase
from centipede.Task import Task
from centipede.TaskWrapper import TaskWrapper
from centipede.Crawler.Fs import FsPath
from centipede.Resource import Resource

class UPythonTest(BaseTestCase):
    """Test UPython subprocess."""

    __sourcePath = os.path.join(BaseTestCase.dataDirectory(), 'test.exr')
    __taskPath = os.path.join(BaseTestCase.dataDirectory(), 'tasks', 'UPythonTestTask.py')

    def testUPythonMultiLevel(self):
        """
        Test that the UPython subprocess works properly when launching it from another subprocess.
        """
        resource = Resource.get()
        resource.load(self.__taskPath)
        crawler = FsPath.createFromPath(self.__sourcePath)
        dummyTask = Task.create('uPythonTestTask')
        dummyTask.add(crawler)
        dummyTask.setOption("runUPython", True)
        wrapper = TaskWrapper.create('upython')
        result = wrapper.run(dummyTask)
        self.assertTrue(len(result), 1)
        self.assertIn("testUPython", result[0].varNames())
        self.assertEqual(result[0].var("testUPython"), OpenImageIO.VERSION)

    def testUPython(self):
        """
        Test that the UPython subprocess works properly.
        """
        resource = Resource.get()
        resource.load(self.__taskPath)
        crawler = FsPath.createFromPath(self.__sourcePath)
        dummyTask = Task.create('uPythonTestTask')
        dummyTask.add(crawler)
        dummyTask.setOption("runUPython", False)
        wrapper = TaskWrapper.create('upython')
        result = wrapper.run(dummyTask)
        self.assertTrue(len(result), 1)
        self.assertIn("testUPython", result[0].varNames())
        self.assertEqual(result[0].var("testUPython"), OpenImageIO.VERSION)


if __name__ == "__main__":
    unittest.main()
