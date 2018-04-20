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

    @staticmethod
    def rfind(fileName, startPath, finalPath=None):
        """
        Find and return a specific file.

        Starts from the "startPath" and it goes backwards until it finds the specified file or reaches the "finalPath".
        If a file is not found, raises an IOError exception.

        :param fileName: The file name to find.
        :type fileName: str
        :param startPath: The path to start.
        :type startPath: str
        :param finalPath: It stops to search when reaching this path.
        :type: finalPath: str
        """
        resultPath = os.path.join(startPath, fileName)
        if os.path.exists(resultPath):
            return resultPath

        if startPath == finalPath or startPath == '/':
            raise IOError('File was not found')

        previousPath = os.path.dirname(startPath)
        return _Path.rfind(fileName, previousPath, finalPath)

    @staticmethod
    def find(fileName, startPath):
        """
        Find and return a specific file.

        Starts from the "startPath" and it goes forwards until it finds the specified file. If a file is not found,
        return an empty string.

        :param fileName: The file name to find.
        :type fileName: str
        :param startPath: The path to start.
        :type startPath: str
        """
        result = ''
        resultPath = os.path.join(startPath, fileName)
        if os.path.exists(resultPath):
            return resultPath

        # When it can not access the next directory (e.g. permissions errors), It raises a StopIteration Error.
        try:
            dirList = next(os.walk(startPath))[1]
        except StopIteration:
            dirList = []

        for dir in dirList:
            nextPath = os.path.join(startPath, dir)
            result = _Path.find(fileName, nextPath)
            if result:
                return result

        return result


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

ExpressionEvaluator.register(
    'rfind',
    _Path.rfind
)

ExpressionEvaluator.register(
    'find',
    _Path.find
)
