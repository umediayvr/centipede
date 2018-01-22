import os
import sys
import json
import tempfile
import subprocess
from .TaskWrapper import TaskWrapper
from ..Task import Task
from ..Crawler.Fs import Path

class SubprocessFailedError(Exception):
    """Subprocess failed Error."""

class Subprocess(TaskWrapper):
    """
    Executes a task inside of a subprocess.
    """

    __serializedTaskEnv = "TASKWRAPPER_SUBPROCESS_FILE"

    def __init__(self):
        """
        Create a task wrapper object.
        """
        super(Subprocess, self).__init__()

        self.setOption('user', '')

    def _commandPrefix(self):
        """
        For re-implementation: should return a string used as prefix for the command executed as subprocess.
        """
        # returning right away when no user is specified
        user = self.option('user')
        if user == '':
            return ''

        # otherwise in case the user starts with '$' means the value is driven by an environment variable.
        if user.startswith('$'):
            user = os.environ[user[1:]]

        # running as different user
        return 'su {} -c'.format(user)

    def _command(self):
        """
        For re-implementation: should return a string which is executed as subprocess.
        """
        return 'upython -c "import ingestor; ingestor.TaskWrapper.Subprocess.runSerializedTask()"'

    def _perform(self, task):
        """
        Implement the execution of the subprocess wrapper.
        """
        # execute proccess passing json
        serializedTaskFile = tempfile.NamedTemporaryFile(suffix='.json').name
        with open(serializedTaskFile, 'w') as f:
            f.write(task.toJson())

        # we need to make this temporary file R&W for anyone, since it may be manipulated by
        # a subprocess that uses a different user/permissions.
        os.chmod(serializedTaskFile, 0o777)

        # building full command executed as subprocess
        command = self._command()
        if self._commandPrefix():
            command = '{} "{}"'.format(
                self._commandPrefix(),
                command.replace('\\', '\\\\').replace('"', '\\"')
            )

        env = dict(os.environ)
        env[self.__serializedTaskEnv] = serializedTaskFile

        # calling task as subprocess
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            shell=True
        )

        # capturing the output
        output, error = process.communicate()
        if output:
            sys.stdout.write(output.decode("utf-8"))
            sys.stdout.flush()

        if error:
            sys.stderr.write(error.decode("utf-8"))
            sys.stderr.flush()

        # checking if process has failed based on the return code
        if process.returncode:
            raise SubprocessFailedError(
                'Error during the execution of the process, return code {}'.format(
                    process.returncode
                )
            )

        # the task passes the result by serializing it as json, we need to load the json file
        # and re-create the crawlers.
        result = []
        with open(serializedTaskFile) as jsonFile:
            for serializedJsonCrawler in json.load(jsonFile):
                result.append(
                    Path.createFromJson(serializedJsonCrawler)
                )

        return result

    @staticmethod
    def runSerializedTask():
        """
        Run a serialized task defined in the environment during Subprocess._perform.
        """
        serializedTaskFilePath = os.environ[Subprocess.__serializedTaskEnv]
        serializedJsonTaskContent = None
        with open(serializedTaskFilePath) as jsonFile:
            serializedJsonTaskContent = jsonFile.read()

        # re-creating the task from the json contents
        task = Task.createFromJson(serializedJsonTaskContent)

        # running task and serializing the output as json.
        serializedCrawlers = []
        for crawler in task.output():
            serializedCrawlers.append(crawler.toJson())

        # we use the environment to tell where the result has been serialized
        # so it can be resulted back by the parent process.
        with open(serializedTaskFilePath, 'w') as f:
            f.write(json.dumps(serializedCrawlers))


# registering task wrapper
TaskWrapper.register(
    'subprocess',
    Subprocess
)
