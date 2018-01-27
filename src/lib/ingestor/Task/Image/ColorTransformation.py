import os
from array import array
from .UpdateImageMetadata import UpdateImageMetadata
from ..Task import Task

class ColorTransformation(Task):
    """
    Applies a color transformation to an image using open color io and open image io.

    Optional Option: "ocioConfig"
    Required Options: "sourceColorSpace" and "targetColorSpace".
    """

    __ocioConfigDefault = ""

    def __init__(self, *args, **kwargs):
        """
        Create a color transformation task.
        """
        super(ColorTransformation, self).__init__(*args, **kwargs)

        self.setOption("ocioConfig", self.__ocioConfigDefault)

    def _perform(self):
        """
        Perform the task.
        """
        import OpenImageIO as oiio
        import PyOpenColorIO as ocio

        # open color io configuration
        if self.option('ocioConfig'):
            config = ocio.Config.CreateFromFile(self.option('ocioConfig'))
        else:
            config = ocio.GetCurrentConfig()

        sourceColorSpace = self.option('sourceColorSpace')
        targetColorSpace = self.option('targetColorSpace')
        metadata = {
            'sourceColorSpace': sourceColorSpace,
            'targetColorSpace': targetColorSpace
        }

        for pathCrawler in self.pathCrawlers():
            # source image
            sourceImage = oiio.ImageInput.open(pathCrawler.var('filePath'))
            spec = sourceImage.spec()
            spec.set_format(oiio.FLOAT)

            pixels = sourceImage.read_image()
            sourceImage.close()

            transformedPixels = config.getProcessor(
                sourceColorSpace,
                targetColorSpace
            ).applyRGB(pixels)

            targetFilePath = self.filePath(pathCrawler)

            # trying to create the directory automatically in case it does not exist
            try:
                os.makedirs(os.path.dirname(targetFilePath))
            except OSError:
                pass

            targetImage = oiio.ImageOutput.create(targetFilePath)

            # umedia metadata information
            UpdateImageMetadata.updateUmediaMetadata(
                spec,
                pathCrawler,
                metadata
            )

            success = targetImage.open(
                targetFilePath,
                spec,
                oiio.Create
            )

            # saving target image
            if success:
                writePixels = array('d')
                writePixels.fromlist(transformedPixels)
                targetImage.write_image(writePixels)
            else:
                raise Exception(oiio.geterror())

        # default result based on the target filePath
        return super(ColorTransformation, self)._perform()


# registering task
Task.register(
    'colorTransformation',
    ColorTransformation
)
