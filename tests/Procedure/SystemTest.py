import unittest
import os
from ..BaseTestCase import BaseTestCase
from centipede.Procedure import Procedure

class SystemTest(BaseTestCase):
    """Test System procedures."""

    def testTmpdir(self):
        """
        Test that the tmpdir procedure works properly.
        """
        result = Procedure.run("tmpdir")
        self.assertFalse(os.path.exists(result))

    def testEnv(self):
        """
        Test that the env procedure works properly.
        """
        result = Procedure.run("env", "USERNAME")
        self.assertEqual(result, os.environ.get("USERNAME"))


if __name__ == "__main__":
    unittest.main()
