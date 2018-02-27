import os
from .Subprocess import Subprocess

class UPython(Subprocess):
    """
    Runs a task through upython.
    """

    def _command(self):
        """
        For re-implementation: should return a string which is executed as subprocess.
        """
        scriptLoaderPath = os.path.join(
            os.path.dirname(
                os.path.realpath(__file__)
            ),
            'aux',
            'runSerializedTask.py'
        )

        return 'upython {}'.format(scriptLoaderPath)


# registering task wrapper
Subprocess.register(
    'upython',
    UPython
)
