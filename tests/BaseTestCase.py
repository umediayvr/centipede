import os
import unittest
import sys

# querying root directory
root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Add ingestor source code to python path for tests
sourceFolder = os.path.join(root, "src", "lib")
if not os.path.exists(sourceFolder):  # pragma: no cover
    raise Exception("Can't resolve lib location!")

sys.path.insert(1, sourceFolder)

class BaseTestCase(unittest.TestCase):
    """Base class for ingestor unit tests."""

    __rootPath = root

    @classmethod
    def rootPath(cls):
        """
        Return the ingestor code root path.
        """
        return cls.__rootPath

    @classmethod
    def dataDirectory(cls):
        """
        Return the directory that contains test data.
        """
        return os.path.join(cls.__rootPath, "data", "tests")
