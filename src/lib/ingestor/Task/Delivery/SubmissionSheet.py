import csv
import os
from ...Crawler.Fs import Path
from ...Crawler.Fs.Image import Image
from ...Crawler.Fs.Video import Video
from ..Task import Task
from ...Template import Template

class SubmissionSheet(Task):
    """
    A task to create a cvs file for client deliveries.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a SubmissionSheet.
        """
        super(SubmissionSheet, self).__init__(*args, **kwargs)

        self.__rows = {}
        self.__deliveryData = {}
        self.__clientDeliveryPath = ""

    def _perform(self):
        """
        Perform the task.
        """
        jsonCrawler = self.pathCrawlers()[0]
        self.__getDeliveryData(jsonCrawler)

        self.__columnLabels = list(map(lambda x: x[0], self.option("_columns")))

        internalDeliveryFolder = os.path.dirname(jsonCrawler.var('filePath'))
        self.__clientDeliveryPath = os.path.join(internalDeliveryFolder, jsonCrawler.var('name'))
        pathCrawler = Path.createFromPath(self.__clientDeliveryPath)
        for pathCrawler in pathCrawler.glob(filterTypes=[Image, Video]):
            self.__setRow(pathCrawler)

        self.__writeSpreadsheet()
        if self.option("includeLogFile"):
            self.__writeLogFile()

        return []

    def __getDeliveryData(self, jsonCrawler):
        """
        Get the delivery data stored in a json file in the parent folder of the client delivery folder.
        """
        self.__deliveryData = jsonCrawler.contents()

    def __setRow(self, pathCrawler):
        """
        Get the data expected to be in a spreadsheet row for the given file crawler.
        """
        name = pathCrawler.var("name")
        isProxy = (name.endswith("_h264") or name.endswith("_prores"))
        if isProxy and not self.option('includeProxies'):
            return

        shortName = name if not isProxy else "_".join(name.split("_")[:-1])
        if shortName not in self.__rows:
            self.__addRow(shortName, pathCrawler)
        else:
            self.__updateRow(shortName, pathCrawler)

    def __addRow(self, name, pathCrawler):

        self.__rows[name] = {}
        for label, fieldName in self.option("_columns"):
            # Deal with fields that require custom processing
            if fieldName == "name":
                self.__rows[name][label] = name

            elif fieldName == "clientStatus":
                var = {"sg_status_list": self.__deliveryData[name].get('sg_status_list')}
                self.__rows[name][label] = Template(self.option('clientStatus')).value(var)

            else:
                self.__rows[name][label] = self.__getFieldValue(name, fieldName, pathCrawler)

    def __updateRow(self, name, pathCrawler):

        for label, fieldName in self.option("_columns"):
            if fieldName == "clientFileType":
                currentExt = self.__rows[name].get(label)
                extName = self.__getFieldValue(name, fieldName, pathCrawler)
                if extName not in currentExt.split(","):
                    self.__rows[name][label] = "{},{}".format(currentExt, extName)

    def __getFieldValue(self, name, fieldName, pathCrawler):
        # Look for a value in the delivery data first
        if fieldName in self.__deliveryData[name]:
            return self.__deliveryData[name].get(fieldName)
        # Next, it could be a task option
        elif fieldName in self.optionNames():
            return Template(self.option(fieldName)).valueFromCrawler(pathCrawler)
        # Finally, the value would be in the crawler
        elif fieldName in pathCrawler.varNames():
            return pathCrawler.var(fieldName)

    def __writeSpreadsheet(self):
        """
        Write a cvs file at the target path.
        """
        targetPath = os.path.join(self.__clientDeliveryPath, "{}.csv".format(self.pathCrawlers()[0].var('name')))
        with open(targetPath, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.__columnLabels)
            writer.writeheader()
            for rowName in self.__rows:
                writer.writerow(self.__rows[rowName])

    def __writeLogFile(self):
        name = os.path.basename(self.__clientDeliveryPath)
        logFile = os.path.join(self.__clientDeliveryPath, "{}_log.txt".format(name))
        os.system("ls -1R {} > {}".format(self.__clientDeliveryPath, logFile))


# registering task
Task.register(
    'submissionSheet',
    SubmissionSheet
)
