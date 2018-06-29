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


class _UPython2(UPython):
    """
    Forces a task to be performed using upython 2.
    """

    def __init__(self, *args, **kwargs):
        super(_UPython2, self).__init__(*args, **kwargs)

        self.setOption('envOverride', {
            "UVER_UPYTHON_VERSION": os.environ['UVER_UPYTHON2_VERSION']
        })

class _UPython3(UPython):
    """
    Forces a task to be performed using upython 3.
    """

    def __init__(self, *args, **kwargs):
        super(_UPython3, self).__init__(*args, **kwargs)

        self.setOption('envOverride', {
            "UVER_UPYTHON_VERSION": os.environ['UVER_UPYTHON3_VERSION']
        })

# registering task wrappers
Subprocess.register(
    'upython',
    UPython
)

# specific for python 2.x
Subprocess.register(
    'upython2',
    _UPython2
)

# specific for python 3.x
Subprocess.register(
    'upython3',
    _UPython3
)
