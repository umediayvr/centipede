import os
from ..Task import Task

class Remove(Task):
    """
    Remove target files task.
    """

    def _perform(self):
        """
        Perform the task.
        """
        for pathCrawler in self.pathCrawlers():
            yield pathCrawler
            filePath = self.filePath(pathCrawler)

            os.remove(filePath)


# registering task
Task.register(
    'remove',
    Remove
)
