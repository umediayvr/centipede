import os
import tempfile
import threading
from ulauncher import ProcessExecution
from ..Dispatcher import Dispatcher

class _ProcessExecutionThread(threading.Thread):
    """
    Thread used to execute the sub-process.
    """

    def __init__(self, processExecution):
        """
        Create a process execution thread.
        """
        assert isinstance(processExecution, ProcessExecution), \
            "Invalid processExecution type!"

        super(_ProcessExecutionThread, self).__init__()
        self.__processExecution = processExecution

    def run(self):
        """
        Run the thread.
        """
        self.__processExecution.execute()

class Local(Dispatcher):
    """
    Local dispatcher implementation.

    Dispatches the task holder as a sub-process and returns
    the proccess id. The sub-process is executed in a separated
    thread by default.
    """

    __runningThreads = []
    __defaultAwaitExecution = False

    def __init__(self, *args, **kwargs):
        """
        Create a local dispatch instance.
        """
        super(Local, self).__init__(*args, **kwargs)

        self.setOption(
            "awaitExecution",
            self.__defaultAwaitExecution
        )

    def _perform(self, taskHolder):
        """
        Execute the dispatcher.
        """
        self.cleanup()

        processExecution = ProcessExecution(
            [
                'upython',
                os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    "aux",
                    "execute-local.py"
                ),
                self.__bakeTaskHolderToJson(taskHolder)
            ],
            self.option('env'),
            shell=True,
            redirectStderrToStdout=True
        )

        # executing process
        if self.option('awaitExecution'):
            processExecution.execute()

        # otherwise delegating the execution to a thread
        else:
            # creating a new thread that is going to deal
            # the process execution
            processThread = _ProcessExecutionThread(processExecution)

            self.__runningThreads.append(processThread)

            # start the thread that is going to execute the process.
            processThread.start()

        return processExecution.pid()

    @classmethod
    def cleanup(cls):
        """
        Clean up all the finished threads from dispatched previously.
        """
        # cleaning up previous threads that have been finished
        for runningThread in list(cls.__runningThreads):
            if not runningThread.is_alive():
                del cls.__runningThreads[runningThread]

    @classmethod
    def __bakeTaskHolderToJson(cls, taskHolder):
        """
        Return the file path for the input serialized taskHolder.
        """
        temporaryFile = tempfile.NamedTemporaryFile(
            mode='w',
            prefix="local_",
            suffix='.json',
            delete=False
        )
        temporaryFile.write(taskHolder.toJson())
        temporaryFile.close()

        return temporaryFile.name


# registering dispatcher
Local.register(
    'local',
    Local
)
