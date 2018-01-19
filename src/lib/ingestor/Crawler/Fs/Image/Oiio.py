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

    def var(self, name):
        """
        Return var value using lazy loading implementation for width and height.
        """
        if name in ['width', 'height'] and name not in self.varNames():
            # alternatively width and height information could come from the
            # parent directory crawler "1920x1080". For more details take a look
            # at "Directory" crawler.
            if hasOpenImageIO:
                imageInput = OpenImageIO.ImageInput.open(self.pathHolder().path())
                spec = imageInput.spec()
                self.setVar('width', spec.width)
                self.setVar('height', spec.height)
                imageInput.close()

        return super(Oiio, self).var(name)
