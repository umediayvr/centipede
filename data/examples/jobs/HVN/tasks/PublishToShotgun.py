import os
import json
import inspect
import shutil
import tempfile
import subprocess
from collections import OrderedDict
from ingestor import Template
from ingestor.Task import Task

class PublishToShotgun(ingestor.Task):
    """
    Publish sequence files to shotgun.
    """

    def _perform(self):
        """
        Perform the task.
        """
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
            configPath = Template("{configPath}").valueFromCrawler(sourceCrawler)

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
                'comment': comment,
                'configPath': configPath
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
                configPath,
                "tasks",
                "aux",
                "runShotgunPublish.py"
            )

            env = dict(os.environ)
            del env['PYTHONPATH']

            process = subprocess.Popen(
                'shotgunpython {pythonFile} {jsonFile}'.format(
                    pythonFile=shotgunPythonFile,
                    jsonFile=shotgunTempFile.name
                ),
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
    'publishToShotgun',
    PublishToShotgun
)
