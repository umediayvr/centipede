from ingestor.Task import Task
from ingestor.TaskWrapper import TaskWrapper

class UPythonTestTask(Task):
    """
    Dummy task for testing UPython subprocess.
    """

    def _perform(self):
        sourceCrawler = self.pathCrawlers()[0]
        if self.option('runUPython'):
            dummyTask = Task.create('uPythonTestTask')
            dummyTask.setOption("runUPython", False)
            dummyTask.add(sourceCrawler)
            wrapper = TaskWrapper.create('upython')
            result = wrapper.run(dummyTask)
        else:
            import OpenImageIO
            sourceCrawler.setVar("testUPython", OpenImageIO.VERSION)
            print("--> Subprocess printout")
            result = [sourceCrawler.clone()]

        return result


Task.register(
    'uPythonTestTask',
    UPythonTestTask
)
