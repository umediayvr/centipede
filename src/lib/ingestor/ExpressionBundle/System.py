import tempfile
import os
from ..ExpressionEvaluator import ExpressionEvaluator

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


# tmp dir
ExpressionEvaluator.register(
    'tmpdir',
    _System.tmpdir
)
