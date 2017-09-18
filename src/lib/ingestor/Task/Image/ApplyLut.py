import os
from array import array
import OpenImageIO as oiio
import PyOpenColorIO as ocio
from ...Template import Template
from ..Task import Task


class ApplyLut(Task):
    """
    Applies a lut to an image using open color io and open image io.

    Options: "lut", "sourceColorSpace" and "targetColorSpace".
    """
    __defaultSourceColorSpace = "lnf"
    __defaultTargetColorSpace = "lnf"

    def __init__(self, *args, **kwargs):
        """
        Create an apply lut object.
        """
        super(ApplyLut, self).__init__(*args, **kwargs)

        self.setOption('sourceColorSpace', self.__defaultSourceColorSpace)
        self.setOption('targetColorSpace', self.__defaultTargetColorSpace)

    def _perform(self):
        """
        Perform the task.
        """

        sourceColorSpace = self.option('sourceColorSpace')
        targetColorSpace = self.option('targetColorSpace')

        for pathCrawler in self.pathCrawlers():
            yield pathCrawler

            config = ocio.GetCurrentConfig().createEditableCopy()
            colorSpace = config.getColorSpace(
                ocio.Constants.ROLE_SCENE_LINEAR
            ).createEditableCopy()

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

            # setting the group transform to the color space
            colorSpace.setTransform(
                groupTransform,
                ocio.Constants.COLORSPACE_DIR_TO_REFERENCE
            )
            config.addColorSpace(colorSpace)

            targetFilePath = self.filePath(pathCrawler)

            # trying to create the directory automatically in case it does not exist
            try:
                os.makedirs(os.path.dirname(targetFilePath))
            except OSError:
                pass

            inputImage = oiio.ImageInput.open(pathCrawler.var('filePath'))
            spec = inputImage.spec()
            spec.set_format(oiio.FLOAT)
            spec.attribute(
                'umedia:lut',
                lut
            )

            pixels = inputImage.read_image()
            inputImage.close()

            transformedPixels = config.getProcessor(groupTransform).applyRGB(pixels)
            outputImage = oiio.ImageOutput.create(targetFilePath)

            success = outputImage.open(
                targetFilePath,
                spec,
                oiio.Create
            )

            if success:
                # ImageInput.read_image() returns a list of floats,
                # and applyRGB(0 returns one too, but ImgOutput.write_image
                # expects an array of float and will die when passed a list.
                pixelArray = array('d')
                pixelArray.fromlist(transformedPixels)

                # saving target image
                outputImage.write_image(pixelArray)
            else:
                raise Exception(oiio.geterror())


# registering task
Task.register(
    'applyLut',
    ApplyLut
)
