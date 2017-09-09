import OpenImageIO as oiio
import os
from ..Task import Task
from collections import OrderedDict

class SequenceThumbnail(Task):
    """
    Creates a thumbnail for the image sequence.
    """
    __defaultWidth = 640
    __defaultHeight = 480

    def __init__(self, *args, **kwargs):
        """
        Create a sequence thumbnail object.
        """
        super(SequenceThumbnail, self).__init__(*args, **kwargs)

        self.setOption('width', self.__defaultWidth)
        self.setOption('height', self.__defaultHeight)

    def _perform(self):
        """
        Perform the task.
        """
        targetThumbnails = OrderedDict()
        for pathCrawler in self.pathCrawlers():
            targetFilePath = self.filePath(pathCrawler)

            if targetFilePath not in targetThumbnails:
                targetThumbnails[targetFilePath] = []

            targetThumbnails[targetFilePath].append(pathCrawler)

        # generating a thumbnail for the sequence
        for targetThumbnail, thumbnailCrawlers in targetThumbnails.items():
            thumbnailCrawler = thumbnailCrawlers[int(len(thumbnailCrawlers) / 2)]

            # creating a thumbnail for the image sequence
            imageThumbnailTask = Task.create('imageThumbnail')
            imageThumbnailTask.add(thumbnailCrawler, targetThumbnail)

            imageThumbnailTask.setOption('width', self.option('width'))
            imageThumbnailTask.setOption('height', self.option('height'))

            for crawler in imageThumbnailTask.run():
                yield crawler


# registering task
Task.register(
    'sequenceThumbnail',
    SequenceThumbnail
)
