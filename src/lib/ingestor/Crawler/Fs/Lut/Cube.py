from .Lut import Lut

class Cube(Lut):
    """
    Cube path crawler.
    """

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a lut file.
        """
        if not super(Cube, cls).test(pathHolder, parentCrawler):
            return False

        return pathHolder.ext() in ['cube', 'ccc', 'cc']


# registration
Cube.register(
    'cube',
    Cube
)
