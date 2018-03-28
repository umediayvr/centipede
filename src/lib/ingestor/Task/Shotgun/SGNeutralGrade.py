import os
import xml.etree.ElementTree as ElementTree
from ..Task import Task
from xml.dom import minidom


class SGNeutralGrade(Task):
    """
    Get the values from neutral grades and update that information in shotgun.
    """

    def _perform(self):
        """
        Perform the task.
        """
        for pathCrawler in self.pathCrawlers():
            targetFilePath = self.filePath(pathCrawler)

            baseDir = os.path.dirname(targetFilePath)
            if not os.path.exists(baseDir):
                os.makedirs(baseDir)

            # writing a xml cc file
            self.__writeXMLFile(pathCrawler, targetFilePath)

            # Publish file in sg

            sgTask = Task.create('sgPublish')
            sgTask.add(pathCrawler, targetFilePath)
            sgTask.setOption('comment', 'Neutral CDL')
            sgTask.setOption('version', 0)
            sgTask.setOption('publishedFileType', 'CC')
            sgTask.setOption('publishName', os.path.basename(targetFilePath))
            sgTask.output()

        return super(SGNeutralGrade, self)._perform()

    def __writeXMLFile(self, pathCrawler, targetFilePath):
        """
        Create a xml file with the same structure as the cc file.

        <ColorCorrection>
           <SOPNode>
              <Slope>1 1 1</Slope>
              <Offset>0 0 0</Offset>
              <Power>1 1 1</Power>
           </SOPNode>
           <SatNode>
              <Saturation>1</Saturation>
           </SatNode>
        </ColorCorrection>

        :param pathCrawler: The crawler that has the information needed to write the xml file
        :type pathCrawler: list
        :param targetFilePath: The path of the file that will be published
        :type targetFilePath: str
        """
        root = ElementTree.Element("ColorCorrection")
        sopNode = ElementTree.SubElement(root, "SOPNode")
        slope = pathCrawler.var("slope")
        offset = pathCrawler.var("offset")
        power = pathCrawler.var("power")
        saturation = pathCrawler.var("saturation")

        ElementTree.SubElement(sopNode, "Slope").text = "{slopeR} {slopeG} {slopeB}".format(
            slopeR=slope[0],
            slopeG=slope[1],
            slopeB=slope[2]
        )
        ElementTree.SubElement(sopNode, "Offset").text = "{offsetR} {offsetG} {offsetB}".format(
            offsetR=offset[0],
            offsetG=offset[1],
            offsetB=offset[2]
        )
        ElementTree.SubElement(sopNode, "Power").text = "{powerR} {powerG} {powerB}".format(
            powerR=power[0],
            powerG=power[1],
            powerB=power[2]
        )

        satNode = ElementTree.SubElement(root, "SatNode")
        ElementTree.SubElement(satNode, "Saturation").text = "{saturation}".format(saturation=saturation)

        # write the file
        xmlstr = minidom.parseString(ElementTree.tostring(root)).toprettyxml(indent="   ")
        with open(targetFilePath, "w") as f:
            f.write(xmlstr)


# registering task
Task.register(
    'sgNeutralGrade',
    SGNeutralGrade
)
