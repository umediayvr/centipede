import os
import shutil
from ..Task import Task


class CopyTargetDirectoryError(Exception):
    """Copy Target Directory Error."""

    pass


class Copy(Task):
    """
    Copies a file to the filePath.
    """

    def _perform(self):
        """
        Perform the task.
        """
        for pathCrawler in self.pathCrawlers():
            filePath = self.filePath(pathCrawler)

            # trying to create the directory automatically in case it does not exist
            try:
                os.makedirs(os.path.dirname(filePath))
            except OSError:
                pass

            # copying the file to the new target
            sourceFilePath = pathCrawler.var('filePath')
            targetFilePath = filePath

            # Check if the target path already exists, if it is file removed it else raise and execption
            if os.path.isfile(targetFilePath):
                os.remove(targetFilePath)
            elif os.path.isdir(targetFilePath):
                raise CopyTargetDirectoryError

            # doing the copy
            shutil.copy2(
                sourceFilePath,
                targetFilePath
            )

        # default result based on the target filePath
        return super(Copy, self)._perform()


# registering task
Task.register(
    'copy',
    Copy
)
