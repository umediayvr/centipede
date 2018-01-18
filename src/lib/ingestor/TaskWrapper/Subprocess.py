import os
import sys
import tempfile
import subprocess
from .TaskWrapper import TaskWrapper
from ..Task import Task

class SubprocessFailedError(Exception):
    """Subprocess failed Error."""

class Subprocess(TaskWrapper):
    """
    Executes a task inside of a subprocess.
    """

    __serializedTaskEnv = "UMEDIA_SUBPROCESS_SERIALIZED_TASK"

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

        # yielding crawler
        for pathCrawler in task.pathCrawlers():
            yield pathCrawler

    @staticmethod
    def runSerializedTask():
        """
        Run a serialized task defined in the environment during Subprocess._perform.
        """
        serializedJsonTaskContent = None
        with open(os.environ[Subprocess.__serializedTaskEnv]) as jsonFile:
            serializedJsonTaskContent = jsonFile.read()

        task = Task.createFromJson(serializedJsonTaskContent)

        # running task
        for pathCrawler in task.run(): pass


# registering task wrapper
TaskWrapper.register(
    'subprocess',
    Subprocess
)
