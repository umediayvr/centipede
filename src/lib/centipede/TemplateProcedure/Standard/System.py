import tempfile
import uuid
import os
from ..TemplateProcedure import TemplateProcedure

class _System(object):
    """
    Basic system functions.
    """

    @staticmethod
    def tmpdir():
        """
        Return a temporary directory path (under the OS temp location).
        """
        path = os.path.join(
            tempfile.gettempdir(),
            str(uuid.uuid4())
        )

        return path

    @staticmethod
    def env(name, defaultValue=''):
        """
        Return the value of an environment variable.
        """
        return os.environ.get(name, defaultValue)


# registering template procedures
TemplateProcedure.register(
    'tmpdir',
    _System.tmpdir
)

TemplateProcedure.register(
    'env',
    _System.env
)
