import os
import time
from ..Task import Task
from ...Crawler.Fs import FsPath
from .CreateData import CreateData

class FileNotUnderDataDirectoryError(Exception):
    """File Not Under Data Directory Error."""

class MetadataNotFoundError(Exception):
    """Metadata Not Found Error."""

class InvalidFileOwnerError(Exception):
    """Invalid File Owner Error."""

class MakeDirsError(Exception):
    """Make Dirs Error."""

class CopyFileError(Exception):
    """Copy File Error."""

class FailedToLockDataError(Exception):
    """Failed To Lock Data Error."""

class CreateVersion(CreateData):
    """
    ABC for creating a version.
    """

    __genericCrawlerInfo = [
        "job",
        "seq",
        "shot",
        "assetName",
        "step",
        "variant"
    ]

    def __init__(self, *args, **kwargs):
        """
        Create a version.
        """
        super(CreateVersion, self).__init__(*args, **kwargs)

        self.__startTime = time.time()
        self.__loadedStaticData = False

    def version(self):
        """
        Return an integer containing the published version.
        """
        return self.__version

    def versionPath(self):
        """
        Return the path for the version base folder.
        """
        return self.rootPath()

    def versionName(self):
        """
        Return the name of the version base folder.
        """
        return os.path.basename(self.versionPath())

    def add(self, *args, **kwargs):
        """
        Cache the static information about the first crawler you add.
        """
        super(CreateVersion, self).add(*args, **kwargs)

        # make sure to do not create any files/directories at this point, since this call does not guarantee
        # the task is going to be executed right away (since tasks can be serialized).
        self.__loadStaticData()

    def output(self):
        """
        Run the task.

        We need to wrap this call to make sure the versionPath is created before
        any of the sub-classes try to write to it through _perform.
        """
        os.makedirs(self.versionPath())

        return super(CreateVersion, self).output()

    def _perform(self):
        """
        Perform the task.
        """
        super(CreateVersion, self)._perform()

        # Find all the crawlers for data that was created for this version
        crawler = FsPath.createFromPath(self.dataPath())
        dataCrawlers = crawler.glob()

        # Add json files
        for jsonFile in ["info.json", "data.json", "env.json"]:
            dataCrawlers.append(FsPath.createFromPath(os.path.join(self.versionPath(), jsonFile)))

        # Add context variables so subsequent tasks get them
        for crawler in dataCrawlers:
            for var in self.__genericCrawlerInfo:
                if var in self.infoNames():
                    crawler.setVar(var, self.info(var), True)
            crawler.setVar("versionPath", self.versionPath(), True)
            crawler.setVar("version", self.version(), True)
            crawler.setVar("versionName", self.versionName(), True)
            crawler.setVar("dataPath", self.dataPath(), True)

        return dataCrawlers

    def updateInfo(self):
        """
        Write info.json file.
        """
        self.addInfo('version', self.version())
        self.addInfo('totalTime', int(time.time() - self.__startTime))

        super(CreateVersion, self).updateInfo()

    def __loadStaticData(self):
        """
        Load the static information about the publish.
        """
        if self.__loadedStaticData or not self.crawlers():
            return

        self.__loadedStaticData = True

        # all crawlers must contain the same information about assetName,
        # variant and version. For this reason looking only in the first one
        crawler = self.crawlers()[0]

        # Add generic info that is expected to be on the crawler
        for info in self.__genericCrawlerInfo:
            if info in crawler.varNames():
                self.addInfo(info, crawler.var(info))

        # looking for the version based on the version folder name
        # that follows the convention "v001"
        self.__version = int(os.path.basename(self.versionPath())[1:])


# registering task
Task.register(
    'createVersion',
    CreateVersion
)
