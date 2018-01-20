import hashlib
from ..Task import Task

class ChecksumMatchError(Exception):
    """Checksum match error."""

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

        # default result based on the target filePath
        return super(Checksum, self)._perform()


# registering task
Task.register(
    'checksum',
    Checksum
)
