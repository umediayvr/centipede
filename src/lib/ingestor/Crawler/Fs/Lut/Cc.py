from .Lut import Lut
from ..Ascii import Xml

class Cc(Lut):
    """
    Parses a Cc file.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a Cc object.
        """
        super(Cc, self).__init__(*args, **kwargs)

        self.__parseXML()

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a lut file.
        """
        if not super(Cc, cls).test(pathHolder, parentCrawler):
            return False

        return pathHolder.ext() == 'cc'

    def __parseXML(self):
        """
        Parse the cc XML information and assign that to the crawler.
        """
        ccTags = ['Slope', 'Offset', 'Power', 'Saturation', 'Error']
        ccRequireTags = ['ColorCorrection', 'SOPNode', 'Error', 'SatNode']

        # Check if the cdl have the required tags
        xmlCrawler = Xml.createFromPath(self.var('filePath'), 'xml')
        for tag in ccRequireTags:
            xmlCrawler.queryTag(tag)

        # Get the values from the cdl file
        for tag in ccTags:
            tagValue = xmlCrawler.queryTag(tag)
            if tag == 'Saturation':
                self.setVar(tag.lower(), float(tagValue))
                continue

            elif tag == 'Error' and tagValue is not None:
                self.setVar(tag.lower(), tagValue)
                continue

            value = list(map(float, tagValue.split(" ")))
            self.setVar(tag.lower(), value)


# registering crawler
Cc.register(
    'cc',
    Cc
)
