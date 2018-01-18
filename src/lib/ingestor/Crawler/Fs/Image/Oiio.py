from .Image import Image

try:
    import OpenImageIO
except ImportError:
    hasOpenImageIO = False
else:
    hasOpenImageIO = True

class Oiio(Image):
    """
    Open image io crawler.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a exr path crawler.
        """
        super(Oiio, self).__init__(*args, **kwargs)

        # alternatively width and height information could come from the
        # parent directory crawler "1920x1080". For more details take a look
        # at "Directory" crawler.
        if hasOpenImageIO:
            self.__imageBuf = OpenImageIO.ImageBuf(self.pathHolder().path())

            spec = self.__imageBuf.spec()
            self.setVar('width', spec.width)
            self.setVar('height', spec.height)

    def imageBuf(self):
        """
        Return the oiio image's buffer for the path.
        """
        assert hasOpenImageIO, "OpenImageIO is not available"

        return self.__imageBuf
