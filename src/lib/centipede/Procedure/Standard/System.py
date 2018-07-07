import tempfile
import os
from ..Procedure import Procedure

class _System(object):
    """
    Basic system functions.
    """

    @staticmethod
    def tmpdir():
        """
        Return a temporary directory path (under the OS temp location).
        """
        path = tempfile.mkdtemp()
        # delete the path so it gets recreated later with the correct user
        os.rmdir(path)
        return path

    @staticmethod
    def env(name, defaultValue=''):
        """
        Return the value of an environment variable.
        """
        return os.environ.get(name, defaultValue)


# registering procedures
Procedure.register(
    'tmpdir',
    _System.tmpdir
)

Procedure.register(
    'env',
    _System.env
)
