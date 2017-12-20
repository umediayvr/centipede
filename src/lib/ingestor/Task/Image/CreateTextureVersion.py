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

    def _perform(self):
        """
        Perform the task.
        """
        textures = {
            "metadata": {}
        }
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

                yield pathCrawler

            targetFilePath = self.filePath(pathCrawler)
            jsonFilePath = targetFilePath

            textureTargetLocation = self.__computeTextureTargetLocation(
                pathCrawler,
                pathCrawler.var('ext')
            )

            if pathCrawler.var('ext') not in textures:
                # trying to create the directory automatically in case it does not exist
                try:
                    os.makedirs(os.path.dirname(textureTargetLocation))
                except OSError:
                    pass

                textures[pathCrawler.var('ext')] = []

            textures[pathCrawler.var('ext')].append(
                os.path.basename(textureTargetLocation)
            )

            sourceTexturePath = pathCrawler.var('filePath')

            # copying the texture file
            shutil.copyfile(
                sourceTexturePath,
                textureTargetLocation
            )

            # now computing tx
            textureTxTargetLocation = self.__computeTextureTargetLocation(
                pathCrawler,
                "tx"
            )

            if "tx" not in textures:
                textures["tx"] = []

                # trying to create the directory automatically in case it does not exist
                try:
                    os.makedirs(os.path.dirname(textureTxTargetLocation))
                except OSError:
                    pass

            textures["tx"].append(
                os.path.basename(textureTxTargetLocation)
            )

            subprocess.call(
                '/data/studio/upipe/plugins/maya/2018/mtoa/2.0.2.3/bin/linux/bin/maketx {0} -o "{2}" "{1}"'.format(
                    self.option("maketxArgs"),
                    textureTargetLocation,
                    textureTxTargetLocation
                ),
                shell=True
            )

        # writting the json file
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
