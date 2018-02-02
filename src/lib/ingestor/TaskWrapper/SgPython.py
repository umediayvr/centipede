import os
from .Subprocess import Subprocess

class SgPython(Subprocess):
    """
    Runs a task through shotgun python.
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
            'runShotgunSerializedTask.py'
        )

        return 'shotgunpython {}'.format(scriptLoaderPath)


# registering task wrapper
Subprocess.register(
    'sgPython',
    SgPython
)
