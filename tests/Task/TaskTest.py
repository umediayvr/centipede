import os
import unittest
from ..BaseTestCase import BaseTestCase
from centipede.Crawler.Fs import FsPath
from centipede.TaskHolderLoader import JsonLoader
from centipede.TaskWrapper import TaskWrapper
from centipede.Task import Task
from centipede.Task.Task import InvalidPathCrawlerError
from centipede.Task.Task import TaskInvalidOptionError
from centipede.Task.Task import TaskInvalidOptionValue
from centipede.Task.Task import TaskTypeNotFoundError
from centipede.TaskHolder import TaskHolderInvalidVarNameError
from centipede.Crawler.Fs.Image import Jpg, Exr
from centipede.Crawler import Crawler

class TaskTest(BaseTestCase):
    """Test for tasks."""

    __jsonConfig = os.path.join(BaseTestCase.dataDirectory(), 'config', 'test.json')

    def testTaskRegistration(self):
        """
        Test that you can register a new Task.
        """
        class DummyTask(Task):
            pass
        Task.register("dummy", DummyTask)
        self.assertIn("dummy", Task.registeredNames())
        self.assertRaises(TaskTypeNotFoundError, Task.create, 'badTask')

    def testTaskPathCrawlers(self):
        """
        Test that path crawlers are correctly associated with tasks.
        """
        dummyTask = Task.create('copy')
        crawlers = FsPath.createFromPath(BaseTestCase.dataDirectory()).glob(['mov'])
        for crawler in crawlers:
            target = '{}_target'.format(crawler.var('name'))
            dummyTask.add(crawler, target)
        self.assertEqual(len(dummyTask.pathCrawlers()), len(crawlers))
        for filterOption in ['0', 'False', 'false']:
            with self.subTest(filterOption=filterOption):
                dummyTask.setOption('filterTemplate', filterOption)
                self.assertFalse(len(dummyTask.pathCrawlers()))
        dummyTask.setOption('filterTemplate', 'randomStr')
        self.assertEqual(len(dummyTask.pathCrawlers()), len(crawlers))
        for crawler in crawlers:
            target = '{}_target'.format(crawler.var('name'))
            self.assertEqual(dummyTask.filePath(crawler), target)
        badCrawler = FsPath.createFromPath(self.__jsonConfig)
        self.assertRaises(InvalidPathCrawlerError, dummyTask.filePath, badCrawler)

    def testTaskClone(self):
        """
        Test that cloning tasks works properly.
        """
        dummyTask = Task.create('sequenceThumbnail')
        crawlers = FsPath.createFromPath(BaseTestCase.dataDirectory()).glob(['exr'])
        for crawler in crawlers:
            target = '{}_target'.format(crawler.var('name'))
            dummyTask.add(crawler, target)
        clone = dummyTask.clone()
        self.assertCountEqual(dummyTask.optionNames(), clone.optionNames())
        self.assertCountEqual(dummyTask.metadataNames(), clone.metadataNames())
        self.assertCountEqual(
            map(dummyTask.filePath, dummyTask.pathCrawlers()),
            map(clone.filePath, clone.pathCrawlers())
        )
        self.assertCountEqual(
            map(lambda x: x.var('filePath'), dummyTask.pathCrawlers()),
            map(lambda x: x.var('filePath'), clone.pathCrawlers())
        )

    def testTaskOptions(self):
        """
        Test that task options are working properly.
        """
        dummyTask = Task.create('copy')
        dummyTask.setOption('boolOption', True)
        self.assertEqual(dummyTask.option('boolOption'), True)
        dummyTask.setOption('floatOption', 1.0)
        self.assertEqual(dummyTask.option('floatOption'), 1.0)
        dummyTask.setOption('intOption', 1)
        self.assertEqual(dummyTask.option('intOption'), 1)
        self.assertRaises(TaskInvalidOptionError, dummyTask.option, 'badOption')

    def testTaskTemplateOption(self):
        """
        Test that task template option are working properly.
        """
        class MyClawler(Crawler):
            pass

        taskHolderLoader = JsonLoader()
        taskHolderLoader.addFromJsonFile(self.__jsonConfig)
        dummyCrawler = MyClawler('dummy')
        dummyCrawler.setVar('testCustomVar', 'testValue')

        for taskHolder in taskHolderLoader.taskHolders():
            vars = {'testCustomVar': taskHolder.var('testCustomVar')}
            dummyTask = taskHolder.task()
            self.assertEqual(dummyTask.templateOption('testOption', crawler=dummyCrawler), 'testValue')
            self.assertEqual(dummyTask.templateOption('testOption', vars=vars), 'randomValue')
            self.assertEqual(dummyTask.templateOption('testExpr'), '2')

    def testTaskOutput(self):
        """
        Test that task output is returned properly.
        """
        class DummyTask(Task):
            pass
        Task.register("dummy", DummyTask)

        dummyTask = Task.create('dummy')
        crawlers = FsPath.createFromPath(BaseTestCase.dataDirectory()).glob(['mov'])
        targetPaths = []
        for crawler in crawlers:
            target = '{}_target.mov'.format(crawler.var('name'))
            targetPath = os.path.join(BaseTestCase.dataDirectory(), target)
            targetPaths.append(targetPath)
            crawler.setVar('contextVarTest', 1, True)
            dummyTask.add(crawler, targetPath)
        result = dummyTask.output()
        self.assertEqual(len(result), len(crawlers))
        self.assertCountEqual(
            map(lambda x: x.var('filePath'), result),
            targetPaths
        )
        self.assertEqual(
            list(map(lambda x: x.var('contextVarTest'), result)),
            [1]*len(crawlers)
        )
        for crawler in result:
            self.assertIn('contextVarTest', crawler.contextVarNames())
        dummyTask.setOption('filterTemplate', 'false')
        dummyTask.setOption('emptyFilterResult', 'empty')
        result = dummyTask.output()
        self.assertEqual(len(result), 0)
        dummyTask.setOption('emptyFilterResult', 'taskCrawlers')
        result = dummyTask.output()
        self.assertCountEqual(
            map(lambda x: x.var('filePath'), result),
            map(lambda x: x.var('filePath'), crawlers)
        )
        dummyTask.setOption('emptyFilterResult', 'badOption')
        self.assertRaises(TaskInvalidOptionValue, dummyTask.output)

    def testTaskJson(self):
        """
        Test that you can convert a Task to json and back.
        """
        class DummyTask(Task):
            pass
        Task.register("dummy", DummyTask)

        dummyTask = Task.create('dummy')
        crawlers = FsPath.createFromPath(BaseTestCase.dataDirectory()).glob(['mov'])
        targetPaths = []
        for crawler in crawlers:
            target = '{}_target.mov'.format(crawler.var('name'))
            targetPath = os.path.join(BaseTestCase.dataDirectory(), target)
            targetPaths.append(targetPath)
            dummyTask.add(crawler, targetPath)
        jsonResult = dummyTask.toJson()
        resultTask = Task.createFromJson(jsonResult)
        self.assertCountEqual(dummyTask.optionNames(), resultTask.optionNames())
        self.assertCountEqual(dummyTask.metadataNames(), resultTask.metadataNames())
        self.assertCountEqual(
            map(lambda x: x.var('filePath'), dummyTask.pathCrawlers()),
            map(lambda x: x.var('filePath'), resultTask.pathCrawlers())
        )
        self.assertCountEqual(
            map(dummyTask.filePath, dummyTask.pathCrawlers()),
            map(resultTask.filePath, resultTask.pathCrawlers())
        )

    def testConfig(self):
        """
        Test that you can run tasks through a config file properly.
        """
        taskHolderLoader = JsonLoader()
        taskHolderLoader.addFromJsonFile(self.__jsonConfig)
        crawlers = FsPath.createFromPath(BaseTestCase.dataDirectory()).glob()

        createdCrawlers = []
        for taskHolder in taskHolderLoader.taskHolders():
            self.assertIn('testCustomVar', taskHolder.varNames())
            self.assertEqual(taskHolder.var('testCustomVar'), 'randomValue')
            self.assertRaises(TaskHolderInvalidVarNameError, taskHolder.var, 'badVar')
            createdCrawlers += taskHolder.run(crawlers)

        exrCrawlers = list(filter(lambda x: isinstance(x, Exr), createdCrawlers))
        self.assertEqual(len(exrCrawlers), 16)

        jpgCrawlers = list(filter(lambda x: isinstance(x, Jpg), createdCrawlers))
        self.assertEqual(len(jpgCrawlers), 1)

        self.cleanup(exrCrawlers + jpgCrawlers)

    def cleanup(self, crawlers):
        """
        Remove the data that was copied.
        """
        removeTask = Task.create('remove')
        for crawler in crawlers:
            removeTask.add(crawler, crawler.var("filePath"))
        wrapper = TaskWrapper.create('subprocess')
        wrapper.setOption('user', '')
        wrapper.run(removeTask)


if __name__ == "__main__":
    unittest.main()
