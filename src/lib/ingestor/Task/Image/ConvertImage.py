import os
from ..Task import Task
from .UpdateImageMetadata import UpdateImageMetadata

class ConvertImage(Task):
    """
    Convert the source image (from the crawler) to the target one using oiio.
    """

    def _perform(self):
        """
        Perform the task.
        """
        import OpenImageIO as oiio

        for pathCrawler in self.pathCrawlers():

            targetFilePath = self.filePath(pathCrawler)

            # trying to create the directory automatically in case it does not exist
            try:
                os.makedirs(os.path.dirname(targetFilePath))
            except OSError:
                pass

            # converting image using open image io
            inputImageFilePath = pathCrawler.var('filePath')
            imageInput = oiio.ImageInput.open(inputImageFilePath)
            inputSpec = imageInput.spec()

            # updating umedia metadata
            UpdateImageMetadata.updateUmediaMetadata(inputSpec, pathCrawler)

            outImage = oiio.ImageOutput.create(targetFilePath)
            outImage.open(
                targetFilePath,
                inputSpec,
                oiio.ImageOutputOpenMode.Create
            )

            outImage.copy_image(imageInput)
            outImage.close()

        # default result based on the target filePath
        return super(ConvertImage, self)._perform()


# registering task
Task.register(
    'convertImage',
    ConvertImage
)
