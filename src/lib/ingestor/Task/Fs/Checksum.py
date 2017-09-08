import os
import shutil
import hashlib
from ..Task import Task

class ChecksumMatchError(Exception):
    "Checksum match error"

class Checksum(Task):
    """
    Make sure the filePath has the same checksum as the crawler file path.

    In case the checksum does not match an expection is raised.
    """

    def _perform(self):
        """
        Perform the task.
        """
        for pathCrawler in self.pathCrawlers():
            yield pathCrawler

            # copying the file to the new target
            sourceFilePath = pathCrawler.var('filePath')
            targetFilePath = self.filePath(pathCrawler)

            # TODO: change md5 for xxHash
            sourceFileHash = hashlib.md5(open(sourceFilePath, 'rb').read()).hexdigest()
            targetFileHash = hashlib.md5(open(targetFilePath, 'rb').read()).hexdigest()

            if sourceFileHash != targetFileHash:
                raise ChecksumMatchError(
                    'Checksum does not match in the target "{0}"'.format(
                        targetFileHash
                    )
                )


# registering task
Task.register(
    'checksum',
    Checksum
)
