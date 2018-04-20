from .Lut import Lut
import re
import xml.etree.ElementTree as ElementTree

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
        tree = ElementTree.parse(self.var('filePath'))
        root = tree.getroot()
        namespace = self.__xmlNamespace(root)

        colorDecision = root.find('{}ColorDecision'.format(namespace))
        colorCorrection = colorDecision.find('{}ColorCorrection'.format(namespace))
        sopNode = colorCorrection.find('{}SOPNode'.format(namespace))

        slope = sopNode.find('{}Slope'.format(namespace))
        offset = sopNode.find('{}Offset'.format(namespace))
        power = sopNode.find('{}Power'.format(namespace))

        slope = list(map(float, slope.text.split(" ")))
        offset = list(map(float, offset.text.split(" ")))
        power = list(map(float, power.text.split(" ")))

        satNode = colorCorrection.find('{}SatNode'.format(namespace))
        saturation = float(satNode.find('{}Saturation'.format(namespace)).text)

        self.setVar('slope', slope)
        self.setVar('offset', offset)
        self.setVar('power', power)
        self.setVar('saturation', saturation)

    @classmethod
    def __xmlNamespace(cls, element):
        """
        Return the namespace used in the xml file.
        """
        m = re.match('\{.*\}', element.tag)
        return m.group(0) if m else ''


# registering crawler
Cdl.register(
    'cdl',
    Cdl
)
