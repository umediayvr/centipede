import os
import re
import sys
from .Path import Path
from ...PathHolder import PathHolder

class Directory(Path):
    """
    Directory path crawler.
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
        Return a bollean telling if the crawler is leaf.
        """
        return False

    def _computeChildren(self):
        """
        Return the directory contents.
        """
        result = []
        currentPath = self.pathHolder().path()
        for childFile in os.listdir(currentPath):

            # skipping any file with an ilegal name
            if not re.match(self.__invalidFileNameRegex, childFile):
                sys.stderr.write(
                    'file ignored: "{}" (invalid characters)\n'.format(
                        os.path.join(currentPath, childFile)
                    )
                )
                continue

            childPathHolder = PathHolder(os.path.join(currentPath, childFile))
            childCrawler = Path.create(childPathHolder, self)
            result.append(childCrawler)

        return result

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a directory.
        """
        return pathHolder.isDirectory()


# registration
Path.register(
    'directory',
    Directory
)
