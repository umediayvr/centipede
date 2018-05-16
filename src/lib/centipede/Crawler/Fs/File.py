from .FsPath import FsPath
from ..Crawler import Crawler

class File(FsPath):
    """
    File path crawler.
    """

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a file.
        """
        if not super(File, cls).test(pathHolder, parentCrawler):
            return False
        return pathHolder.isFile()


# registration (it's registered as generic, rather than 'file' to show
# that there is no specialized crawler when a file is marked with
# with this type)
Crawler.register(
    'generic',
    File
)
