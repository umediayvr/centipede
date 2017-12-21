import os
from ..Task import Task

class Chmod(Task):
    """
    Chmod task that can be operated over a single file or over a directory path recursively.

    Require options: mode (444 for read-only)
    """

    def _perform(self):
        """
        Perform the task.
        """
        alreadyDone = set()
        octalMode = int(str(self.option('mode')), 8)
        for pathCrawler in self.pathCrawlers():
            yield pathCrawler
            filePath = self.filePath(pathCrawler)

            if alreadyDone in alreadyDone:
                continue

            collectedFiles = self.__collectAllFiles(filePath)
            collectedFiles.sort(reverse=True)

            for collectedFile in collectedFiles:

                if os.path.islink(collectedFile):
                    continue

                os.chmod(collectedFile, octalMode)

    @classmethod
    def __collectAllFiles(cls, path):
        """
        Return all files recursively from the given path.
        """
        result = [path]

        if os.path.isdir(path):
            for entry in os.listdir(path):
                fullPath = os.path.join(path, entry)
                if os.path.isdir(fullPath):
                    result += cls.__collectAllFiles(fullPath)
                else:
                    result.append(fullPath)
        return result


# registering task
Task.register(
    'chmod',
    Chmod
)
