import sys
from centipede.Task import Task

class UPythonMajorVerTestTask(Task):
    """
    Dummy task for testing python 2 subprocess.
    """

    def _perform(self):
        sourceCrawler = self.crawlers()[0]
        sourceCrawler.setVar("majorVer", sys.version_info[0])
        return [sourceCrawler.clone()]


Task.register(
    'uPythonMajorVerTestTask',
    UPythonMajorVerTestTask
)
