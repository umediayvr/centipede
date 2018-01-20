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
            filePath = self.filePath(pathCrawler)

            os.remove(filePath)

        # default result based on the target filePath
        return super(Remove, self)._perform()


# registering task
Task.register(
    'remove',
    Remove
)
