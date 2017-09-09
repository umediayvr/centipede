import os
import shutil
from ..Task import Task

class Copy(Task):
    """
    Copies a file to the filePath.
    """

    def _perform(self):
        """
        Perform the task.
        """
        for pathCrawler in self.pathCrawlers():
            yield pathCrawler
            filePath = self.filePath(pathCrawler)

            # trying to create the directory automatically in case it does not exist
            try:
                os.makedirs(os.path.dirname(filePath))
            except OSError:
                pass

            # copying the file to the new target
            sourceFilePath = pathCrawler.var('filePath')
            targetFilePath = filePath

            # doing the copy
            shutil.copy2(
                sourceFilePath,
                targetFilePath
            )


# registering task
Task.register(
    'copy',
    Copy
)
