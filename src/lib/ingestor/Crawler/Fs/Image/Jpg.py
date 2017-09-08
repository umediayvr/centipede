from .Oiio import Oiio

class Jpg(Oiio):
    """
    Jpg path crawler.
    """

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains an jpg file.
        """
        if not super(Jpg, cls).test(pathHolder, parentCrawler):
            return False

        return pathHolder.ext() == 'jpg'


# registration
Jpg.register(
    'jpg',
    Jpg
)
