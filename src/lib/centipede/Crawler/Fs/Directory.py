import os
import re
import sys
from .FsPath import FsPath
from ...PathHolder import PathHolder
from ..Crawler import Crawler

class Directory(FsPath):
    """
    Directory crawler.
    """

    # checking for digits as prefix separated by x or X and finishing with digits as suffix
    __resolutionRegex = '^[0-9]+[x|X][0-9]+$'

    # checking if the string contains any space
    __invalidFileNameRegex = '^\S+$'

    def __init__(self, *args, **kwargs):
        """
        Create a directory crawler.
        """
        super(Directory, self).__init__(*args, **kwargs)

        # in case the directory has a name "<width>x<height>" lets extract
        # this information and assign that to variables
        if re.match(self.__resolutionRegex, self.var('name')):
            width, height = map(int, self.var('name').lower().split('x'))

            # making sure it contains at least a QVGA resolution, otherwise
            # ignore it
            if width >= 320 and height >= 240:
                self.setVar('width', width)
                self.setVar('height', height)

    def isLeaf(self):
        """
        Return a boolean telling if the crawler is leaf.
        """
        return False

    def _computeChildren(self):
        """
        Return the directory contents.
        """
        result = []
        currentPath = self.pathHolder().path()
        for childFile in os.listdir(currentPath):

            # skipping any file with an illegal name
            if not re.match(self.__invalidFileNameRegex, childFile):
                sys.stderr.write(
                    'file ignored: "{}" (invalid characters)\n'.format(
                        os.path.join(currentPath, childFile)
                    )
                )
                continue

            childPathHolder = PathHolder(os.path.join(currentPath, childFile))
            childCrawler = Crawler.create(childPathHolder, self)
            result.append(childCrawler)

        return result

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a directory.
        """
        if not super(Directory, cls).test(pathHolder, parentCrawler):
            return False
        return pathHolder.isDirectory()


# registration
Crawler.register(
    'directory',
    Directory
)
