import unittest
from ..BaseTestCase import BaseTestCase
from centipede.TemplateProcedure import TemplateProcedure

class ImageSequenceTest(BaseTestCase):
    """Test ImageSequence template procedures."""

    def testPadding(self):
        """
        Test that the padding procedure works properly.
        """
        padding = TemplateProcedure.run("pad", 1, 4)
        self.assertEqual(padding, "0001")
        padding = TemplateProcedure.run("pad", 100, 6)
        self.assertEqual(padding, "000100")

    def testRetimePadding(self):
        """
        Test that the retime padding procedure works properly.
        """
        padding = TemplateProcedure.run("retimepad", 1, 5, 4)
        self.assertEqual(padding, "0006")
        padding = TemplateProcedure.run("retimepad", 100, -99, 6)
        self.assertEqual(padding, "000001")


if __name__ == "__main__":
    unittest.main()
