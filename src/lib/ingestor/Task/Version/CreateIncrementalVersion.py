import os
import json
from ..Task import Task
from .CreateVersion import CreateVersion

class CreateIncrementalVersion(CreateVersion):
    """
    ABC for creating an incremental version.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a version.
        """
        super(CreateIncrementalVersion, self).__init__(*args, **kwargs)
        self.setOption('incremental', True)
        self.setOption('incrementalSpecificVersion', 0)

    def addFile(self, filePath, metadata=None):
        """
        Add a file a published to the version.

        This information is used to write "files.json" where
        metadata information can be associated with the file through metadata
        parameter passed as dictionary.
        """
        if metadata is None:
            metadata = {}

        # including source version on the incremental metadata
        if 'sourceVersion' not in metadata:
            metadata['sourceVersion'] = self.version()

        super(CreateIncrementalVersion, self).addFile(
            filePath,
            metadata
        )

    def addIncrementalFiles(self, version):
        """
        Add files under localized under input version to the current version as hardlink.
        """
        # building the incremental version full path
        incrementalVersionPath = os.path.join(
            os.path.dirname(self.versionPath()),
            'v{0}'.format(str(version).zfill(3))
        )

        incrementalVersionData = os.path.join(
            incrementalVersionPath,
            "data.json"
        )

        # making sure the incremental version exists
        if not os.path.exists(incrementalVersionData):
            return

        # getting all file paths from the current version
        currentVersionRelativeFilePaths = list(map(
            lambda x: x[len(self.versionPath()) + 1:],
            self.files()
        ))

        incrementalVersionContents = json.load(open(incrementalVersionData))
        for fileEntry, fileMetadata in incrementalVersionContents.items():

            # file is part of the current version, skipping it
            if fileEntry in currentVersionRelativeFilePaths:
                continue

            sourceFile = os.path.join(incrementalVersionPath, fileEntry)
            targetFile = os.path.join(self.versionPath(), fileEntry)

            # making sure the target directory exists
            if not os.path.exists(os.path.dirname(targetFile)):
                os.makedirs(os.path.dirname(targetFile))

            # making hardlink
            os.link(sourceFile, targetFile)

            # adding file to the version
            self.addFile(targetFile, fileMetadata)

    def _perform(self):
        """
        Perform the task.
        """
        # when incremental is enabled
        if self.option('incremental'):
            # previous version by default
            incrementalVersion = self.version() - 1

            # unless a custom version has been specified
            if self.option('incrementalSpecificVersion'):
                incrementalVersion = self.option('incrementalSpecificVersion')

            self.addIncrementalFiles(incrementalVersion)

        # source version info
        sourceVersions = set()
        for metadata in list(map(self.fileMetadata, self.files())):
            sourceVersions.add(metadata['sourceVersion'])
        self.addInfo('sourceVersions', list(sourceVersions))

        # calling super class
        return super(CreateIncrementalVersion, self)._perform()


# registering task
Task.register(
    'createIncrementalVersion',
    CreateIncrementalVersion
)
