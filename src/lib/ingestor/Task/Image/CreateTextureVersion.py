import os
import json
import shutil
import subprocess
from ..Task import Task

class CreateTextureVersion(Task):
    """
    Create the texture version.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a texture version.
        """
        super(CreateTextureVersion, self).__init__(*args, **kwargs)
        self.setOption('maketxArgs', "-v -u --unpremult --oiio")
        self.setOption('incremental', True)
        self.setOption('incrementalSpecificVersion', 0)

    def _perform(self):
        """
        Perform the task.
        """
        textures = {
            "metadata": {},
            "files": {}
        }
        sourceVersions = set()
        totalSize = 0

        jsonFilePath = None
        for pathCrawler in self.pathCrawlers():

            if jsonFilePath is None:
                assetName = pathCrawler.var("assetName")
                variant = pathCrawler.var("variant")
                version = int(
                    os.path.basename(
                        os.path.dirname(self.filePath(pathCrawler))
                    )[1:]
                )

                textures["metadata"]["assetName"] = assetName
                textures["metadata"]["variant"] = variant
                textures["metadata"]["version"] = version
                textures["metadata"]["sourceVersions"] = sourceVersions
                sourceVersions.add(version)

                yield pathCrawler

            jsonFilePath = self.filePath(pathCrawler)
            ext = pathCrawler.var('ext')

            textureTargetLocation = self.__computeTextureTargetLocation(
                pathCrawler,
                ext
            )

            if ext not in textures["files"]:
                # trying to create the directory automatically in case it does not exist
                try:
                    os.makedirs(os.path.dirname(textureTargetLocation))
                except OSError:
                    pass

                textures["files"][ext] = {}

            sourceTexturePath = pathCrawler.var('filePath')

            # copying the texture file
            shutil.copyfile(
                sourceTexturePath,
                textureTargetLocation
            )

            textureLocation = os.path.basename(textureTargetLocation)
            textureSize = os.stat(textureTargetLocation).st_size
            textures["files"][ext][textureLocation] = {
                "sourceVersion": textures["metadata"]["version"],
                "size": textureSize
            }
            totalSize += textureSize

            # now computing tx
            textureTxTargetLocation = self.__computeTextureTargetLocation(
                pathCrawler,
                "tx"
            )

            if "tx" not in textures["files"]:
                textures["files"]["tx"] = {}

                # trying to create the directory automatically in case it does not exist
                try:
                    os.makedirs(os.path.dirname(textureTxTargetLocation))
                except OSError:
                    pass

            subprocess.call(
                '/data/studio/upipe/plugins/maya/2018/mtoa/2.0.2.3/bin/linux/bin/maketx {0} -o "{2}" "{1}"'.format(
                    self.option("maketxArgs"),
                    textureTargetLocation,
                    textureTxTargetLocation
                ),
                shell=True
            )

            txSize = os.stat(textureTxTargetLocation).st_size
            textures["files"]["tx"][os.path.basename(textureTxTargetLocation)] = {
                "sourceVersion": textures["metadata"]["version"],
                "size": txSize
            }
            totalSize += txSize

            # creating hardlinks
            if self.option('incremental'):

                previousVersion = textures['metadata']['version'] - 1
                if self.option('incrementalSpecificVersion'):
                    previousVersion = self.option('incrementalSpecificVersion')

                previousVersion = 'v{0}'.format(str(previousVersion).zfill(3))
                previousVersionFile = os.path.join(
                    os.path.dirname(os.path.dirname(self.filePath(pathCrawler))),
                    previousVersion,
                    os.path.basename(jsonFilePath)
                )

                # looking at the versions
                if os.path.exists(previousVersionFile):
                    previousVersionContents = json.load(open(previousVersionFile))
                    for textureType in previousVersionContents['files'].keys():
                        # comparing textures
                        if textureType not in textures["files"]:
                            textures["files"][textureType] = {}

                        # creating relative hard links
                        for textureFileName in previousVersionContents["files"][textureType].keys():
                            if textureFileName not in textures["files"][textureType]:
                                # make hardlink
                                textures["files"][textureType][textureFileName] = previousVersionContents["files"][textureType][textureFileName]
                                sourceVersions.add(textures["files"][textureType][textureFileName]['sourceVersion'])
                                totalSize += textures["files"][textureType][textureFileName]['size']

                                os.link(
                                    os.path.join(
                                        os.path.dirname(os.path.dirname(jsonFilePath)),
                                        previousVersion,
                                        textureType,
                                        os.path.basename(textureFileName)
                                    ),
                                    os.path.join(
                                        os.path.dirname(jsonFilePath),
                                        textureType,
                                        os.path.basename(textureFileName)
                                    ),
                                )

        textures["metadata"]["size"] = totalSize
        textures["metadata"]["sourceVersions"] = list(textures["metadata"]["sourceVersions"])

        # writing json file
        with open(jsonFilePath, 'w') as jsonOutFile:
            json.dump(textures, jsonOutFile, indent=4, sort_keys=True)

    def __computeTextureTargetLocation(self, crawler, ext):
        """
        Compute the target file path for an texture.
        """
        targetFilePath = self.filePath(crawler)

        return os.path.join(
            os.path.dirname(targetFilePath),
            ext,
            "{0}_{1}.{2}".format(
                crawler.var('mapType'),
                crawler.var('udim'),
                ext
            )
        )


# registering task
Task.register(
    'createTextureVersion',
    CreateTextureVersion
)
