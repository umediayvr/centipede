from .Path import Path

class File(Path):
    """
    File path crawler.
    """

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a file.
        """
        return pathHolder.isFile()


# registration (it's registered as generic, rather than 'file' to show
# that there is no specialized crawler when a file is marked with
# with this type)
Path.register(
    'generic',
    File
)
