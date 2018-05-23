import unittest
from ..BaseTestCase import BaseTestCase
from ingestor.ExpressionEvaluator import ExpressionEvaluator

class ImageSequenceTest(BaseTestCase):
    """Test ImageSequence expressions."""

    def testPadding(self):
        """
        Test that the padding expression works properly.
        """
        padding = ExpressionEvaluator.run("pad", 1, 4)
        self.assertEqual(padding, "0001")
        padding = ExpressionEvaluator.run("pad", 100, 6)
        self.assertEqual(padding, "000100")

    def testRetimePadding(self):
        """
        Test that the retime padding expression works properly.
        """
        padding = ExpressionEvaluator.run("retimepad", 1, 5, 4)
        self.assertEqual(padding, "0006")
        padding = ExpressionEvaluator.run("retimepad", 100, -99, 6)
        self.assertEqual(padding, "000001")


if __name__ == "__main__":
    unittest.main()
