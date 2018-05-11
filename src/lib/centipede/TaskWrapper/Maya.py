from .TaskWrapper import TaskWrapper
from .DCC import DCC

class Maya(DCC):
    """
    Performs a task inside maya.
    """

    def _command(self):
        """
        For re-implementation: should return a string which is executed as subprocess.
        """
        return 'maya -batch -command "python(\\"import centipede; centipede.TaskWrapper.Subprocess.runSerializedTask()\\")"'

    @classmethod
    def _hookName(cls):
        """
        For re-implementation: should return a string containing the name used for the hook registered in basetools.
        """
        return "maya"


# registering task wrapper
TaskWrapper.register(
    'maya',
    Maya
)
