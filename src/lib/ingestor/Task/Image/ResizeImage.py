import os
import multiprocessing
import OpenImageIO as oiio
from ..Task import Task


class ResizeImage(Task):
    """
    Resizes the image to the sizes defined by the options "width" and "height".

    TODO: missing to umedia metadata/source image attributes.
    """

    def _perform(self):
        """
        Perform the task.
        """
        width = self.option('width')
        height = self.option('height')

        for pathCrawler in self.pathCrawlers():
            yield pathCrawler

            targetFilePath = self.filePath(pathCrawler)

            # trying to create the directory automatically in case it does not exist
            try:
                os.makedirs(os.path.dirname(targetFilePath))
            except OSError:
                pass

            # opening the source image to generate a resized image
            inputImageBuf = oiio.ImageBuf(pathCrawler.var('filePath'))
            inputSpec = inputImageBuf.spec()

            # output spec
            outputSpec = oiio.ImageSpec(
                width,
                height,
                inputSpec.nchannels,
                oiio.FLOAT
            )

            # resized image buf
            resizedImageBuf = oiio.ImageBuf(
                outputSpec
            )

            # resizing image
            oiio.ImageBufAlgo.resize(
                resizedImageBuf,
                inputImageBuf,
                nthreads=multiprocessing.cpu_count()
            )

            # saving target resized image
            resizedImageBuf.write(targetFilePath)


# registering task
Task.register(
    'resizeImage',
    ResizeImage
)
