import os
import json
import tempfile
from ..Task import Task
from ...Crawler.Fs.FsPath import FsPath
from .NukeScript import NukeScript

class NukeTemplate(NukeScript):
    """
    Executes a nuke scene by triggering the write nodes.

    Required options: template (full path of the nuke scene)

    Please checkout the base class for further information about the options.

    TODO: this task needs to be ported to use nuke task wrapper.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a nuke template task.
        """
        super(NukeTemplate, self).__init__(*args, **kwargs)

        self.setOption(
            'script',
            os.path.join(
                os.path.dirname(
                    os.path.realpath(__file__)
                ),
                "aux",
                "loadTemplate.py"
            )
        )

    def add(self, pathCrawler, filePath=''):
        """
        Add a path crawler to the task.
        """
        # this task can be also used to generate a quicktime movie. Therefore,
        # we only split it when creating image sequences. For this reason we
        # need to look if the target file path contains the padding prefix used
        # by nuke to write an image sequence (for instance: "image.%04d.exr").
        if not self.hasMetadata('dispatch.split') and "%0" in filePath:
            self.setMetadata('dispatch.split', True)

        return super(NukeTemplate, self).add(pathCrawler, filePath)

    def _perform(self):
        """
        Execute the task.
        """
        # this option needs to be assigned at this point, otherwise
        # by setting at the construction time the same file name can be
        # shared on the farm when a task is computed in chunks
        self.setOption(
            '_renderOutputData',
            tempfile.NamedTemporaryFile(suffix='.json').name
        )

        super(NukeTemplate, self)._perform()

        # we want to return a list of crawlers about the files that were
        # created during the execution (render) of the nuke file
        # which can be multiple write nodes.
        fileList = []
        with open(self.option('_renderOutputData')) as jsonFile:
            fileList = json.load(jsonFile)

        # no longer need the render output data file
        os.remove(self.option('_renderOutputData'))

        return list(map(FsPath.createFromPath, fileList))


# registering task
Task.register(
    'nukeTemplate',
    NukeTemplate
)
