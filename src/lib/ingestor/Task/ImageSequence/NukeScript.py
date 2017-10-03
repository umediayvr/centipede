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
        Executes nuke script.
        """
        # collecting all crawlers that have the same target file path
        sequenceFiles = OrderedDict()
        for pathCrawler in self.pathCrawlers():
            targetFilePath = self.filePath(pathCrawler)

            if targetFilePath not in sequenceFiles:
                sequenceFiles[targetFilePath] = []

            sequenceFiles[targetFilePath].append(pathCrawler)

        # calling nuke script
        for targetSequenceName, sequenceCrawlers in sequenceFiles.items():
            pathCrawler = sequenceCrawlers[0]
            startFrame = sequenceCrawlers[0].var('frame')
            endFrame = sequenceCrawlers[-1].var('frame')

            # nuke script is about to start
            yield pathCrawler

            # generating a temporary file that is going to contain the options
            # that should be used by nuke script
            tempJsonOptionsFile = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".json",
                mode='w'
            )

            # resolving options
            options = {
                'sequence': targetSequenceName,
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
            process = subprocess.Popen(
                'nuke -x -t "{scriptLoader}" --ingestor-options "{optionsFile}"'.format(
                    scriptLoader=scriptLoaderPath,
                    optionsFile=tempJsonOptionsFile.name
                ),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ,
                shell=True
            )

            # capturing the output
            output, error = process.communicate()

            # removing the temporary file
            os.unlink(tempJsonOptionsFile.name)

            # in case of any erros
            if error:
                raise Exception(error)


# registering task
Task.register(
    'nukeScript',
    NukeScript
)
