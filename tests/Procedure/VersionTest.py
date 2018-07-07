import unittest
import os
from ..BaseTestCase import BaseTestCase
from centipede.Procedure import Procedure

class VersionTest(BaseTestCase):
    """Test Version procedures."""

    def testNewVersion(self):
        """
        Test that the new procedure works properly.
        """
        result = Procedure.run("newver", BaseTestCase.dataDirectory())
        self.assertEqual(result, "v003")

    def testLatestVersion(self):
        """
        Test that the latest version is found properly.
        """
        result = Procedure.run("latestver", BaseTestCase.dataDirectory())
        self.assertEqual(result, "v002")
        result = Procedure.run("latestver", os.path.join(BaseTestCase.dataDirectory(), "glob"))
        self.assertEqual(result, "v000")


if __name__ == "__main__":
    unittest.main()
