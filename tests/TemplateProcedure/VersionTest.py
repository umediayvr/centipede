import unittest
import os
from ..BaseTestCase import BaseTestCase
from centipede.TemplateProcedure import TemplateProcedure

class VersionTest(BaseTestCase):
    """Test Version template procedures."""

    def testNewVersion(self):
        """
        Test that the new procedure works properly.
        """
        result = TemplateProcedure.run("newver", BaseTestCase.dataDirectory())
        self.assertEqual(result, "v003")

    def testLatestVersion(self):
        """
        Test that the latest version is found properly.
        """
        result = TemplateProcedure.run("latestver", BaseTestCase.dataDirectory())
        self.assertEqual(result, "v002")
        result = TemplateProcedure.run("latestver", os.path.join(BaseTestCase.dataDirectory(), "glob"))
        self.assertEqual(result, "v000")


if __name__ == "__main__":
    unittest.main()
