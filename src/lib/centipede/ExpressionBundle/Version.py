import os
import re
from ..ExpressionEvaluator import ExpressionEvaluator

class _Version(object):
    """
    Basic version expressions.

    The versionsPath is usually specified using <parentPath> token.
    """

    @staticmethod
    def new(versionsPath):
        """
        Return a new version.
        """
        version = _Version.__queryLatest(versionsPath)

        return 'v' + str(version + 1).zfill(3)

    @staticmethod
    def latest(versionsPath):
        """
        Return a new version, in case none version is found it returns v000.
        """
        version = _Version.__queryLatest(versionsPath)

        return 'v' + str(version).zfill(3)

    @staticmethod
    def __queryLatest(versionsPath):
        """
        Return the latest version found under the versions path.

        In case none version is found, it returns 0 by default.
        """
        version = 0
        versionRegEx = "^v[0-9]{3}$"

        # finding the latest version
        if os.path.exists(versionsPath):
            for directory in os.listdir(versionsPath):
                if re.match(versionRegEx, directory):
                    version = max(int(directory[1:]), version)

        return version


# new version expression
ExpressionEvaluator.register(
    'newver',
    _Version.new
)

# latest version expression
ExpressionEvaluator.register(
    'latestver',
    _Version.latest
)
