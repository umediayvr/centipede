import os
import json
import tempfile
import subprocess
from collections import OrderedDict
from ..Task import Task
from ...Template import Template

# compatibility with python 2/3
try:
    basestring
except NameError:
    basestring = str

class NukeScript(Task):
    """
    Abstracted nuke python script task.

    The options defined in the task are resolved (in case the value contains a template)
    before passing them to the nuke python script. The script that should be executed by the task
    inside nuke must be defined as one of the options by the name: "script", for instance:
    option['script'] = "myscript.py"

    Reading options inside of nuke, the options are available as a global "options":
    myOption = options['myOption']
    """

    def __init__(self, *args, **kwargs):
        """
        Create a nuke script task.
        """
        super(NukeScript, self).__init__(*args, **kwargs)

        self.__assignMetadata()

    def _perform(self):
        """
        Execute the nuke script.
        """
        # collecting all crawlers that have the same target file path
        sequenceFiles = OrderedDict()
        for pathCrawler in self.pathCrawlers():
            targetFilePath = self.filePath(pathCrawler)

            if targetFilePath not in sequenceFiles:
                sequenceFiles[targetFilePath] = []

            sequenceFiles[targetFilePath].append(pathCrawler)

        # calling nuke script
        for targetSequenceFilePath, sequenceCrawlers in sequenceFiles.items():
            pathCrawler = sequenceCrawlers[0]
            startFrame = sequenceCrawlers[0].var('frame')
            endFrame = sequenceCrawlers[-1].var('frame')
            targetSequenceFilePath = self.filePath(pathCrawler)

            # nuke does not create folders at render time, creating them
            # beforehand
            requiredRenderDirName = os.path.dirname(targetSequenceFilePath)
            if not os.path.exists(requiredRenderDirName):
                try:
                    os.makedirs(requiredRenderDirName)
                except OSError:
                    pass

            # converting the active frame to the frame padding notation
            sourceSequenceFilePath = pathCrawler.var('filePath').split(".")
            sourceSequenceFilePath = '{0}.{1}.{2}'.format(
                '.'.join(sourceSequenceFilePath[:-2]),
                ("#" * len(sourceSequenceFilePath[-2])),
                sourceSequenceFilePath[-1]
            )

            # generating a temporary file that is going to contain the options
            # that should be used by nuke script
            tempJsonOptionsFile = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".json",
                mode='w'
            )

            # resolving options
            options = {
                'sourceSequence': sourceSequenceFilePath,
                'targetSequence': targetSequenceFilePath,
                'startFrame': startFrame,
                'endFrame': endFrame
            }

            for optionName in self.optionNames():
                optionValue = self.option(optionName)

                # resolving template if necessary...
                if isinstance(optionValue, basestring):
                    options[optionName] = Template(optionValue).valueFromCrawler(
                        pathCrawler
                    )
                else:
                    options[optionName] = optionValue

            # writing options
            tempJsonOptionsFile.write(json.dumps(options))
            tempJsonOptionsFile.close()

            # script loader location (this script triggers the nuke script)
            scriptLoaderPath = os.path.join(
                os.path.dirname(
                    os.path.realpath(__file__)
                ),
                'aux',
                'nukeScriptLoader.py'
            )

            # calling nuke
            customEnv = dict(os.environ)

            # delete variable due to a crash with nuke configuration
            if 'OCIO' in customEnv:
                del customEnv['OCIO']

            process = subprocess.Popen(
                'nuke -x -t "{scriptLoader}" --centipede-options "{optionsFile}" --log-level error'.format(
                    scriptLoader=scriptLoaderPath,
                    optionsFile=tempJsonOptionsFile.name
                ),
                env=customEnv,
                shell=True
            )

            # capturing the output
            process.communicate()

            # removing the temporary file
            os.unlink(tempJsonOptionsFile.name)

            # in case of any erros
            if process.returncode:
                raise Exception('Nuke has returned an error code: {}'.format(process.returncode))

        # default result based on the target filePath
        return super(NukeScript, self)._perform()

    def __assignMetadata(self):
        """
        Assign the default metadata to the task.
        """
        # group metadata
        self.setMetadata(
            'dispatch.renderFarm.group',
            os.environ.get(
                'CENTIPEDE_DISPATCHER_RENDERFARM_NUKE_GROUP',
                ''
            )
        )

        # pool metadata
        self.setMetadata(
            'dispatch.renderFarm.pool',
            os.environ.get(
                'CENTIPEDE_DISPATCHER_RENDERFARM_NUKE_POOL',
                ''
            )
        )


# registering task
Task.register(
    'nukeScript',
    NukeScript
)
