from ..Task import Task

class ImageThumbnail(Task):
    """
    Generates a thumbnail for the input image keeping the spect ratio.
    """

    __defaultWidth = 640
    __defaultHeight = 480

    def __init__(self, *args, **kwargs):
        """
        Create a image thumbnail object.
        """
        super(ImageThumbnail, self).__init__(*args, **kwargs)

        self.setOption('width', self.__defaultWidth)
        self.setOption('height', self.__defaultHeight)

    def _perform(self):
        """
        Perform the task.
        """
        width = self.option('width')
        height = self.option('height')

        result = []
        for pathCrawler in self.pathCrawlers():
            targetFilePath = self.filePath(pathCrawler)

            # creating a task to resize the thumbnail
            resizeImageTask = Task.create('resizeImage')
            resizeImageTask.add(pathCrawler, targetFilePath)

            # Calculate resize ratios for resizing
            currentWidth = pathCrawler.var('width')
            currentHeigth = pathCrawler.var('height')

            ratioWidth = width / float(currentWidth)
            ratioHeight = height / float(currentHeigth)

            # smaller ratio will ensure that the image fits in the view
            ratio = ratioWidth if ratioWidth < ratioHeight else ratioHeight

            newWidth = int(currentWidth * ratio)
            newHeight = int(currentHeigth * ratio)

            resizeImageTask.setOption(
                'width',
                newWidth
            )

            resizeImageTask.setOption(
                'height',
                newHeight
            )

            # running task
            result += resizeImageTask.output()

        return result


# registering task
Task.register(
    'imageThumbnail',
    ImageThumbnail
)
