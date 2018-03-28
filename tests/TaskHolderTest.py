import os
import unittest
import glob
from .BaseTestCase import BaseTestCase
from ingestor.Crawler.Fs import Path
from ingestor.TaskHolderLoader import JsonLoader
from ingestor.TaskWrapper import TaskWrapper
from ingestor.Task import Task

class TaskHolderTest(BaseTestCase):
    """Test TaskHolder."""

    __jsonConfig = os.path.join(BaseTestCase.dataDirectory(), 'config', 'test.json')

    def testConfig(self):
        """
        Test that you can run tasks through a config file properly.
        """
        taskHolderLoader = JsonLoader()
        taskHolderLoader.addFromJsonFile(self.__jsonConfig)
        crawlers = Path.createFromPath(BaseTestCase.dataDirectory()).glob()
        for taskHolder in taskHolderLoader.taskHolders():
            taskHolder.run(crawlers)

    @classmethod
    def tearDownClass(cls):
        """
        Remove the data that was copied.
        """
        # find images to delete
        pathCrawler = Path.createFromPath(cls.__jsonConfig)
        dummyTask = Task.create('remove')
        for crawler in pathCrawler.globFromParent(['jpg']):
            dummyTask.add(crawler, crawler.var("filePath"))
        wrapper = TaskWrapper.create('subprocess')
        wrapper.setOption('user', '$UMEDIA_VERSION_PUBLISHER_USER')
        wrapper.run(dummyTask)


if __name__ == "__main__":
    unittest.main()
