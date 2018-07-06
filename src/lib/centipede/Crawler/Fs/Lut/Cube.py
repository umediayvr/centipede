from .Lut import Lut

class Cube(Lut):
    """
    Cube crawler.

    TODO: this crawler is no longer necessary, it is going to be deprecated in
    future releases.
    """

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a lut file.
        """
        if not super(Cube, cls).test(pathHolder, parentCrawler):
            return False

        return pathHolder.ext() in ['cube', 'ccc', 'cc', 'cdl']


# registration
Cube.register(
    'cube',
    Cube
)
