from collections import OrderedDict
from .FFmpeg import FFmpeg
from ..Task import Task

class MovGen(FFmpeg):
    """
    Creates a mov file from an image sequence.
    """

    def _perform(self):
        """
        Perform the task.
        """
        # collecting all crawlers that have the same target file path
        movFiles = OrderedDict()
        for pathCrawler in self.pathCrawlers():
            targetFilePath = self.filePath(pathCrawler)

            if targetFilePath not in movFiles:
                movFiles[targetFilePath] = []

            movFiles[targetFilePath].append(pathCrawler)

        # generating mov files
        for movFile in movFiles.keys():
            sequenceCrawlers = movFiles[movFile]
            pathCrawler = sequenceCrawlers[0]

            # checking target extension
            if not movFile.endswith('.mov'):
                raise Exception(
                    'Target movie name is not a quick time (.mov): "{0}"'.format(
                        movFile
                    )
                )

            # mov generation is about to start
            yield pathCrawler

            # executing ffmpeg
            self.executeFFmpeg(
                map(lambda x: x.var('filePath'), sequenceCrawlers),
                movFile
            )


# registering task
Task.register(
    'movGen',
    MovGen
)
