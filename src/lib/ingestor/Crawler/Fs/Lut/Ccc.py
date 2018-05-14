from .Lut import Lut
from ..Ascii import Xml

class Ccc(Lut):
    """
    Parses a Ccc file.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a Ccc object.
        """
        super(Ccc, self).__init__(*args, **kwargs)

        self.__parseXML()

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a lut file.
        """
        if not super(Ccc, cls).test(pathHolder, parentCrawler):
            return False

        return pathHolder.ext() == 'ccc'

    def __parseXML(self):
        """
        Parse the ccc file (XML file format) information and assign that to the crawler.
        """
        cccTags = ['Slope', 'Offset', 'Power', 'Saturation', 'Error']
        cccRequireTags = ['ColorCorrection', 'SOPNode', 'Error', 'SatNode']

        # Check if the cdl have the required tags
        xmlCrawler = Xml.createFromPath(self.var('filePath'), 'xml')
        for tag in cccRequireTags:
            xmlCrawler.queryTag(tag)

        # Get the values from the cdl file
        for tag in cccTags:
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
Ccc.register(
    'ccc',
    Ccc
)
