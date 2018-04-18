import os
import json
import tempfile
from ...Crawler.Fs import Path
from ..Task import Task
from .NukeScript import NukeScript

class NukeTemplate(NukeScript):
    """
    Executes a nuke scene by triggering the write nodes.

    Required options: template (full path of the nuke scene)

    Please checkout the base class for further information about the options.
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

        self.setOption(
            '_renderOutputData',
            tempfile.NamedTemporaryFile(suffix='.json').name
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
        super(NukeTemplate, self)._perform()

        # we want to return a list of crawlers about the files that were
        # created during the execution (render) of the nuke file
        # which can be multiple write nodes.
        fileList = []
        with open(self.option('_renderOutputData')) as jsonFile:
            fileList = json.load(jsonFile)

        # no longer need the render output data file
        os.remove(self.option('_renderOutputData'))

        return list(map(Path.createFromPath, fileList))


# registering task
Task.register(
    'nukeTemplate',
    NukeTemplate
)
