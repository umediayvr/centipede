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

    @staticmethod
    def parentdirname(string):
        """
        Return the dir name of the parent folder from the full path file.
        """
        return _Path.dirname(_Path.dirname(string))

    @staticmethod
    def basename(string):
        """
        Return the base name from a full path file.
        """
        return os.path.basename(string)


# registering expressions
ExpressionEvaluator.register(
    'dirname',
    _Path.dirname
)

ExpressionEvaluator.register(
    'parentdirname',
    _Path.parentdirname
)

ExpressionEvaluator.register(
    'basename',
    _Path.basename
)
