from .Video import Video

class Mov(Video):
    """
    Mov path crawler.
    """

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a mov file.
        """
        if not super(Mov, cls).test(pathHolder, parentCrawler):
            return False

        return pathHolder.ext() == 'mov'


# registration
Mov.register(
    'mov',
    Mov
)
