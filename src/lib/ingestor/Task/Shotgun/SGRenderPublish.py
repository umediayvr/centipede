import os
import json
import tempfile
import subprocess
from ..Task import Task

class SGRenderPublish(Task):
    """
    Publish a render to shotgun.

    Optional Options: publishedFileType and comment.
    """

    __defaultPublishedFileType = "Render"
    __defaultComment = "render publish"

    def __init__(self, *args, **kwargs):
        """
        Create a RenderPublish object.
        """
        super(SGRenderPublish, self).__init__(*args, **kwargs)

        self.setOption('publishedFileType', self.__defaultPublishedFileType)
        self.setOption('comment', self.__defaultComment)

    def _perform(self):
        """
        Perform the task.
        """
        currentFolder = os.path.dirname(os.path.realpath(__file__))

        sourceCrawler = tuple(self.pathCrawlers())[0]
        versionFolder = sourceCrawler.var("filePath")

        # metadata information about the version
        info = json.load(open(os.path.join(versionFolder, "info.json")))
        seq = info["seq"]
        shot = info["shot"]
        variant = info["variant"]
        version = info["version"]

        # get version, assetName, variant from json contents under info
        output = {
            'job': sourceCrawler.var('job'),
            'seq': seq,
            'shot': shot,
            'name': "{}-render".format(variant),
            'jsonFile': os.path.join(versionFolder, "data.json"),
            'publishedFileType': self.option('publishedFileType'),
            'version': version,
            'comment': self.option('comment')
        }

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
            "runRenderPublish.py"
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
            raise Exception(error)

        # this task does not return any crawlers as result
        return []


# registering task
Task.register(
    'sgRenderPublish',
    SGRenderPublish
)
