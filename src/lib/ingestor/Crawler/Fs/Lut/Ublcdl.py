from .Lut import Lut
import os
import re


class CdlInfo(Lut):
    """
    Child crawler created by the xxxx crawler.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a CdlInfo crawler.
        """
        super(CdlInfo, self).__init__(*args, **kwargs)

        cdlFile = os.path.dirname(self.var('filePath'))
        name = os.path.basename(self.var('filePath'))
        self.load(cdlFile, name)

    def load(self, cdlFile, name):
        with open(cdlFile, 'r') as edlFile:
            data = edlFile.readlines()

        for info in map(lambda x: x.replace('\n', ''), data):

            splitInfo = info.split('\t')

            # Getting the shot name
            plateName = os.path.basename(splitInfo[0]).split('_')[0]
            project = splitInfo[0].split('/')[1]
            seq = plateName[:3].upper()
            shotNumer = plateName[3:]
            shotName = '-'.join((project, seq, shotNumer))

            if shotName != name:
                continue

            cdlInfo = splitInfo[1].split(' ')
            if len(cdlInfo) != 10:
                continue

            self.setVar('slope', list(map(float, [cdlInfo[0], cdlInfo[1], cdlInfo[2]])))
            self.setTag('group', os.path.basename(cdlFile))
            self.setVar('offset', list(map(float, [cdlInfo[3], cdlInfo[4], cdlInfo[5]])))
            self.setVar('power', list(map(float, [cdlInfo[6], cdlInfo[7], cdlInfo[8]])))
            self.setVar('saturation', float(cdlInfo[9]))
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
        For re-implementation: Return a bollean telling if the crawler is leaf.
        """
        return False

    def children(self):
        """
        Return a list of crawlers.
        """
        result = []

        for name in self.__childrenNames():
            # create new crawler, addd that infomration to the crawler
            result.append(self.createFromPath(os.path.join(self.var('filePath'), name)))

        return result

    def __childrenNames(self):
        """
        Create a list of child names
        """
        with open(self.var('filePath'), 'r') as edlFile:
            data = edlFile.readlines()

        result = []
        for info in map(lambda x: x.replace('\n', ''), data):
            splitInfo = info.split('\t')
            plateName = os.path.basename(splitInfo[0]).split('_')[0]
            project = splitInfo[0].split('/')[1]
            seq = plateName[:3].upper()
            shotNumer = plateName[3:]
            shotName = '-'.join((project, seq, shotNumer))
            result.append(shotName)

        return result


# registering crawler
Lut.register(
    'ublcdl',
    Ublcdl
)

Lut.register(
    'cdlInfo',
    CdlInfo
)
