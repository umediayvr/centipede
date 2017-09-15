import os
from ..ExpressionEvaluator import ExpressionEvaluator

class _Path(object):
    """
    Basic path functions.
    """

    @staticmethod
    def dirname(string):
        """
        Return the dir name from a full path file.
        """
        return os.path.dirname(string)


# dir ame
ExpressionEvaluator.register(
    'dirname',
    _Path.dirname
)
