from .Lut import Lut
import os
import re


def getShotName(filePath):
    """
    Compose a shot name base on the file path.

    File path example:
    %C/SKY/IO/incoming/2018_03/03132018/fer0640_plt001_v001/3424x2202_EXR-ZIP/fer0640_plt001_v001.%.4F.exr

    :param info: The information to get the shot name from.
    :type info: str
    """

    plateName = os.path.basename(filePath).split('_')[0]
    project = filePath.split('/')[1]
    seq = plateName[:3].upper()
    shotNumber = plateName[3:]
    shotName = '-'.join((project, seq, shotNumber))

    return shotName


class CdlInfo(Lut):
    """
    Child crawler created by the Ublcdl crawler.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a CdlInfo crawler.
        """
        super(CdlInfo, self).__init__(*args, **kwargs)

        cdlFile, name = os.path.split(self.var('filePath'))
        self.load(cdlFile, name)

    def load(self, cdlFile, name):
        """
        Load the file that have the cdl grades per shot and assign the cdl variables.

        :param cdlFile: The filePath of the cdl filePath
        :type cdlFile: str
        :param name: The name of the shot been process
        :type name: str
        """
        with open(cdlFile, 'r') as edlFile:
            data = edlFile.readlines()

        # Example line cdlFile: /foo/bar/baz/fileName.%.4F.exr	1 1 1 -0.1 -0.1 -0.1 1 1 1 1
        for info in map(lambda x: x.replace('\n', ''), data):
            splitInfo = info.split('\t')

            # Getting the shot name
            shotName = getShotName(splitInfo[0])

            if shotName != name:
                continue

            # The information of the cdl are exactly 10 values, (slope, offset, power)*3 + saturation
            cdlInfo = splitInfo[1].split()
            if len(cdlInfo) != 10:
                continue

            # cdl variables
            self.setTag('group', os.path.basename(cdlFile))
            self.setVar('slope', list(map(float, [cdlInfo[0], cdlInfo[1], cdlInfo[2]])))
            self.setVar('offset', list(map(float, [cdlInfo[3], cdlInfo[4], cdlInfo[5]])))
            self.setVar('power', list(map(float, [cdlInfo[6], cdlInfo[7], cdlInfo[8]])))
            self.setVar('saturation', float(cdlInfo[9]))
            self.setVar('version', 0)
            break

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a cdl file.
        """
        if not super(CdlInfo, cls).test(pathHolder, parentCrawler):
            return False

        return os.path.dirname(pathHolder.path()).endswith('.ublcdl')


class Ublcdl(Lut):
    """
    Parses a Ublcdl file.
    """

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a cdl file.
        """
        if not super(Ublcdl, cls).test(pathHolder, parentCrawler):
            return False

        return pathHolder.ext() == 'ublcdl'

    def isLeaf(self):
        """
        For re-implementation: Return a boolean telling if the crawler is leaf.
        """
        return False

    def children(self):
        """
        Return a list of crawlers.
        """
        result = []

        for name in self.__childNames():
            # Create new crawler, add that information to the crawler
            result.append(self.createFromPath(os.path.join(self.var('filePath'), name)))

        return result

    def __childNames(self):
        """
        Create a list of child names.
        """
        with open(self.var('filePath'), 'r') as edlFile:
            data = edlFile.readlines()

        result = []
        for info in map(lambda x: x.replace('\n', ''), data):
            splitInfo = info.split('\t')
            shotName = getShotName(splitInfo[0])
            result.append(shotName)

        return result


# registering crawlers
Lut.register(
    'ublcdl',
    Ublcdl
)

Lut.register(
    'cdlInfo',
    CdlInfo
)
