import os
import json
import tempfile
import subprocess
from collections import OrderedDict
from ..Task import Task
from ...Template import Template

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
                os.makedirs(requiredRenderDirName)

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
                if isinstance(optionValue, str):
                    options[optionName] = Template(optionValue).valueFromCrawler(
                        pathCrawler
                    )
                else:
                    options[optionName] = optionValue

            # writting options
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
            customEvn = dict(os.environ)

            # delete variable due to a crashing with nuke configuration
            if 'OCIO' in customEvn:
                del customEvn['OCIO']

            process = subprocess.Popen(
                'nuke -x -t "{scriptLoader}" --ingestor-options "{optionsFile}" --log-level error'.format(
                    scriptLoader=scriptLoaderPath,
                    optionsFile=tempJsonOptionsFile.name
                ),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=customEvn,
                shell=True
            )

            # capturing the output
            output, error = process.communicate()

            # removing the temporary file
            os.unlink(tempJsonOptionsFile.name)

            # in case of any erros
            if error:
                raise Exception(error)

        # default result based on the target filePath
        return super(NukeScript, self)._perform()


# registering task
Task.register(
    'nukeScript',
    NukeScript
)
