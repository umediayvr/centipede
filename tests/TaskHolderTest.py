import os
import unittest
from .BaseTestCase import BaseTestCase
from ingestor.Crawler.Fs import Path
from ingestor.TaskHolderLoader import JsonLoader
from ingestor.TaskWrapper import TaskWrapper
from ingestor.Task import Task
from ingestor.Crawler.Fs.Image import Jpg

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
        jpgCrawlers = Path.createFromPath(self.__jsonConfig).globFromParent(['jpg'])
        self.assertEqual(len(jpgCrawlers), 1)
        self.assertIsInstance(jpgCrawlers[0], Jpg)
        # TODO: Assert you can't delete it
        self.addCleanup(self.cleanup, jpgCrawlers[0])

    def cleanup(self, crawler):
        """
        Remove the data that was copied.
        """
        removeTask = Task.create('remove')
        removeTask.add(crawler, crawler.var("filePath"))
        wrapper = TaskWrapper.create('subprocess')
        wrapper.setOption('user', '$UMEDIA_VERSION_PUBLISHER_USER')
        wrapper.run(removeTask)


if __name__ == "__main__":
    unittest.main()
