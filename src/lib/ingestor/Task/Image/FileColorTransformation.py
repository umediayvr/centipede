import os
from array import array
from .UpdateImageMetadata import UpdateImageMetadata
from ...Template import Template
from ..Task import Task

class FileColorTransformation(Task):
    """
    Applies a color transformation to an image using open color io and open image io.

    Optional Option: "ocioConfig"
    Required Options: "sourceColorSpace", "targetColorSpace" and "lut"
    """

    __ocioConfigDefault = ""

    def __init__(self, *args, **kwargs):
        """
        Create a file color transformation task.
        """
        super(FileColorTransformation, self).__init__(*args, **kwargs)

        self.setOption("ocioConfig", self.__ocioConfigDefault)

    def _perform(self):
        """
        Perform the task.
        """
        import OpenImageIO as oiio
        import PyOpenColorIO as ocio

        sourceColorSpace = self.option('sourceColorSpace')
        targetColorSpace = self.option('targetColorSpace')
        metadata = {
            'sourceColorSpace': sourceColorSpace,
            'targetColorSpace': targetColorSpace
        }

        # open color io configuration
        if self.option('ocioConfig'):
            config = ocio.Config.CreateFromFile(self.option('ocioConfig'))
        else:
            config = ocio.GetCurrentConfig()

        for pathCrawler in self.pathCrawlers():
            # resolving the lut path
            lut = Template(self.option('lut')).valueFromCrawler(
                pathCrawler
            )

            # adding color space transform
            groupTransform = ocio.GroupTransform()
            groupTransform.push_back(
                ocio.ColorSpaceTransform(
                    src=sourceColorSpace,
                    dst=targetColorSpace
                )
            )

            # adding lut transform
            groupTransform.push_back(
                 ocio.FileTransform(
                    lut,
                    interpolation=ocio.Constants.INTERP_LINEAR
                 )
            )

            # source image
            sourceImage = oiio.ImageInput.open(pathCrawler.var('filePath'))
            spec = sourceImage.spec()
            spec.set_format(oiio.FLOAT)

            metadata['lutFile'] = lut

            pixels = sourceImage.read_image()
            sourceImage.close()

            transformedPixels = config.getProcessor(
                groupTransform
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
        return super(FileColorTransformation, self)._perform()


# registering task
Task.register(
    'fileColorTransformation',
    FileColorTransformation
)
