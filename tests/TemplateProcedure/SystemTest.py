import unittest
import os
from ..BaseTestCase import BaseTestCase
from centipede.TemplateProcedure import TemplateProcedure

class SystemTest(BaseTestCase):
    """Test System template procedures."""

    def testTmpdir(self):
        """
        Test that the tmpdir procedure works properly.
        """
        result = TemplateProcedure.run("tmpdir")
        self.assertFalse(os.path.exists(result))

    def testEnv(self):
        """
        Test that the env procedure works properly.
        """
        result = TemplateProcedure.run("env", "USERNAME")
        self.assertEqual(result, os.environ.get("USERNAME"))


if __name__ == "__main__":
    unittest.main()
