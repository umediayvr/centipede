import os
import json
import tempfile
import subprocess
from collections import OrderedDict
from ..Task import Task
from ...Template import Template

class SGImageSeqPublish(Task):
    """
    Publish an image sequence to shotgun.

    Required Options: movieFile and thumbnailFile.
    Optional Options: publishedFileType, sceneFile, comment and taskName.
    """

    __defaultPublishedFileType = "Rendered Image"
    __defaultComment = "sequence publish"

    def __init__(self, *args, **kwargs):
        """
        Create an ImageSeqPublish object.
        """
        super(SGImageSeqPublish, self).__init__(*args, **kwargs)

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
            movieFilePath = self.templateOption('movieFile', crawler=sourceCrawler)
            thumbnailFilePath = self.templateOption('thumbnailFile', crawler=sourceCrawler)
            comment = sourceCrawler.var('comment') if 'comment' in sourceCrawler.varNames() else self.option('comment')
            sceneFilePath = sourceCrawler.var('filePath')
            sgTask = sourceCrawler.var('_sgTask') if '_sgTask' in sourceCrawler.varNames() else None
            publishedFileType = self.option('publishedFileType')

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

            output = {
                'job': sourceCrawler.var('job'),
                'name': sourceCrawler.var('renderName'),
                'sequenceNameFormated': sequenceNameFormated,
                'firstFrame': firstFrame,
                'lastFrame': lastFrame,
                'totalFrames': totalFrames,
                'movieFilePath': movieFilePath,
                'thumbnailFilePath': thumbnailFilePath,
                'sceneFilePath': sceneFilePath,
                'publishedFileType': publishedFileType,
                'version': int(version),
                'comment': comment,
                '_sgTask': sgTask
            }

            # generating a temporary file that is going to contain the publish data
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
                "runImageSeqPublish.py"
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

        # this task does not return any crawlers as result
        return []


# registering task
Task.register(
    'sgImageSeqPublish',
    SGImageSeqPublish
)
