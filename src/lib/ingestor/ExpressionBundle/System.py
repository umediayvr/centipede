import tempfile
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
        return tempfile.mkdtemp()


# tmp dir
ExpressionEvaluator.register(
    'tmpdir',
    _System.tmpdir
)
