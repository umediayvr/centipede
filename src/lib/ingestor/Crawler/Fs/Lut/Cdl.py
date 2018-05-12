from .Lut import Lut
from ..Ascii import Xml

class Cdl(Lut):
    """
    Parses a cdl file.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a Cdl object.
        """
        super(Cdl, self).__init__(*args, **kwargs)

        self.__parseXML()

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a cdl file.
        """
        if not super(Cdl, cls).test(pathHolder, parentCrawler):
            return False

        return pathHolder.ext() == 'cdl'

    def __parseXML(self):
        """
        Parse the cld XML information and assign that to the crawler.
        """
        cdlTags = ['Slope', 'Offset', 'Power', 'Saturation']
        cdlRequireTags = ['ColorCorrection', 'SOPNode']

        # Check if the cdl have the required tags
        xmlCrawler = Xml.createFromPath(self.var('filePath'), 'xml')
        for tag in cdlRequireTags:
            xmlCrawler.queryTag(tag)

        # Get the values from the cdl file
        for tag in cdlTags:
            tagValue = xmlCrawler.queryTag(tag)
            value = list(map(float, tagValue.split(" ")))
            if tag == 'Saturation':
                value = value[0]
            self.setVar(tag.lower(), value)


# registering crawler
Cdl.register(
    'cdl',
    Cdl
)
