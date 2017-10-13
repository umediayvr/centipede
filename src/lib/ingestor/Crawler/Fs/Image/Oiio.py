import OpenImageIO
from .Image import Image

class Oiio(Image):
    """
    Open image io crawler.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a exr path crawler.
        """
        super(Oiio, self).__init__(*args, **kwargs)

        # reading width/height from the file
        self.__imageBuf = OpenImageIO.ImageBuf(self.pathHolder().path())

        spec = self.__imageBuf.spec()
        self.setVar('width', spec.width)
        self.setVar('height', spec.height)

    def imageBuf(self):
        """
        Return the oiio image's buffer for the path.
        """
        return self.__imageBuf
