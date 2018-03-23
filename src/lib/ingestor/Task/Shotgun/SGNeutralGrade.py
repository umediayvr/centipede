import os
import xml.etree.ElementTree as ElementTree
from collections import OrderedDict
from ..Task import Task
from xml.dom import minidom


class SGNeutralGrade(Task):
    """
    Get the values from neutral grades and update that information in shotgun
    """

    def _perform(self):
        """
        Perform the task.
        """
        sourceSequenceCrawlers = OrderedDict()
        for pathCrawler in self.pathCrawlers():
            targetFilePath = self.filePath(pathCrawler)

            baseDir = os.path.dirname(targetFilePath)
            if not os.path.exists(baseDir):
                os.makedirs(baseDir)

            project = pathCrawler.var("job")
            shot = pathCrawler.var("shot")
            seq = pathCrawler.var("seq")

            # writting a xml ccc file
            self.__writeXMLFile(pathCrawler, targetFilePath)

            # Publish file in sg
            self.__publishFileInSG(project, shot, targetFilePath)

        return super(SGNeutralGrade, self)._perform()

    def __writeXMLFile(self, pathCrawler, targetFilePath):
        """
        Creates a xml file with the same structure as the ccc file.

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

        :param pathCrawler: The crawler that have all the informatioon need it to write the xml file
        :type pathCrawler: list
        :param targetFilePath: The path of the file that will be publish it
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

    def __publishFileInSG(self, project, shot, targetFilePath):
        """
        Publish a file linked to a specific shot and project

        :param project: The name of the project
        :type project: str
        :param shot: The name of the shot
        :type shot: str
        :param targetFilePath: The path of the file that will be publish it
        :type targetFilePath: str
        """
        from ushotgun import Session
        sg = Session.get()

        sgProject = sg.find_one(
            'Project',
            [['name', 'is', project]],
            []
        )

        filters = [['code', 'is', shot], ['project', 'is', sgProject]]
        # Shotgun operations
        sgShot = sg.find_one(
            'Shot',
            filters,
            []
        )

        sgFileType = sg.find_one('PublishedFileType', filters=[["code", "is", "CCC"]])

        data = {
            'entity': sgShot,
            'path': {'local_path': targetFilePath},
            'published_file_type': sgFileType,
            'name': os.path.basename(targetFilePath),
            'code': os.path.basename(targetFilePath),
            'project': sgProject

        }
        sg.create('PublishedFile', data)


# registering task
Task.register(
    'sgNeutralGrade',
    SGNeutralGrade
)
