import unittest
import os
from ..BaseTestCase import BaseTestCase
from centipede.Task import Task
from centipede.TaskWrapper import TaskWrapper
from centipede.Crawler.Fs import Path
from centipede.Resource import Resource

class SgPythonTest(BaseTestCase):
    """Test SgPython subprocess."""

    __sourcePath = os.path.join(BaseTestCase.dataDirectory(), "test.exr")
    __taskPath = os.path.join(BaseTestCase.dataDirectory(), "tasks", "SgPythonTestTask.py")

    def testSgPython(self):
        """
        Test that the SgPython subprocess works properly.
        """
        resource = Resource.get()
        resource.load(self.__taskPath)
        pathCrawler = Path.createFromPath(self.__sourcePath)
        dummyTask = Task.create('sgPythonTestTask')
        dummyTask.add(pathCrawler)
        self.assertRaises(ModuleNotFoundError, dummyTask.output)

        wrapper = TaskWrapper.create("sgPython")
        result = wrapper.run(dummyTask)
        self.assertTrue(len(result), 1)
        self.assertIn("testVar", result[0].varNames())
        self.assertEqual(result[0].var("testVar"), os.environ.get("UMEDIA_SHOTGUN_URL"))


if __name__ == "__main__":
    unittest.main()
