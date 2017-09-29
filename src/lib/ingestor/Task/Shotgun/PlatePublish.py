import os
import json
import inspect
import shutil
import tempfile
import subprocess
from collections import OrderedDict
from ..Task import Task
from ...Template import Template

class PlatePublish(Task):
    """
    Publish a plate to shotgun.

    Required Options: movieFile and thumbnailFile.
    Optional Options: publishedFileType, comment and taskName.
    """
    __defaultPublishedFileType = "Scan"
    __defaultComment = "plate publish"

    def __init__(self, *args, **kwargs):
        """
        Create a PlatePublish object.
        """
        super(PlatePublish, self).__init__(*args, **kwargs)

        self.setOption('publishedFileType', self.__defaultPublishedFileType)
        self.setOption('comment', self.__defaultComment)

    def _perform(self):
        """
        Perform the task.
        """
        currentFolder = os.path.dirname(os.path.realpath(__file__))

        sourceSequenceCrawlers = OrderedDict()
        for pathCrawler in self.pathCrawlers():
            targetFilePath = self.filePath(pathCrawler)
            if targetFilePath not in sourceSequenceCrawlers:
                sourceSequenceCrawlers[targetFilePath] = []
            sourceSequenceCrawlers[targetFilePath].append(pathCrawler)

        # publishing sequences to shotgun
        for target, sequenceCrawlers in sourceSequenceCrawlers.items():
            sourceCrawler = sequenceCrawlers[0]
            movieFilePath = Template(self.option('movieFile')).valueFromCrawler(sourceCrawler)
            thumbnailFilePath = Template(self.option('thumbnailFile')).valueFromCrawler(sourceCrawler)
            publishedFileType = self.option('publishedFileType')
            comment = self.option('comment')

            version = sourceCrawler.var('version')
            firstFrame = sequenceCrawlers[0].var('frame')
            lastFrame = sequenceCrawlers[-1].var('frame')
            totalFrames = (lastFrame - firstFrame) + 1
            sequenceNameFormated = os.path.join(
                os.path.dirname(sourceCrawler.var('filePath')),
                '{0}.%0{1}d.{2}'.format(
                    sourceCrawler.var('name'),
                    sourceCrawler.var('padding'),
                    sourceCrawler.var('ext')
                )
            )

            yield sourceCrawler
            output = {
                'job': sourceCrawler.var('job'),
                'name': sourceCrawler.var('plateName'),
                'sequenceNameFormated': sequenceNameFormated,
                'firstFrame': firstFrame,
                'lastFrame': lastFrame,
                'totalFrames': totalFrames,
                'movieFilePath': movieFilePath,
                'thumbnailFilePath': thumbnailFilePath,
                'publishedFileType': publishedFileType,
                'version': version,
                'comment': comment
            }

            # generating a temporary file that is going to contain the frames
            # that should be processed by ffmpeg
            shotgunTempFile = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".json",
                mode='w'
            )

            shotgunTempFile.write(json.dumps(output))
            shotgunTempFile.close()

            shotgunPythonFile = os.path.join(
                currentFolder,
                "aux",
                "runPlatePublish.py"
            )

            env = dict(os.environ)
            del env['PYTHONPATH']

            command = 'shotgunpython {pythonFile} {jsonFile}'.format(
                pythonFile=shotgunPythonFile,
                jsonFile=shotgunTempFile.name
            )

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                shell=True
            )

            # capturing the output
            output, error = process.communicate()

            # removing the temporary file
            os.unlink(shotgunTempFile.name)

            # in case of any erros
            if error:
                print(error)


# registering task
Task.register(
    'platePublish',
    PlatePublish
)
