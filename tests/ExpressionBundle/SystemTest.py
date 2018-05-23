import unittest
import os
from ..BaseTestCase import BaseTestCase
from ingestor.ExpressionEvaluator import ExpressionEvaluator

class SystemTest(BaseTestCase):
    """Test System expressions."""

    def testTmpdir(self):
        """
        Test that the tmpdir expression works properly.
        """
        result = ExpressionEvaluator.run("tmpdir")
        self.assertFalse(os.path.exists(result))

    def testEnv(self):
        """
        Test that the env expression works properly.
        """
        result = ExpressionEvaluator.run("env", "USERNAME")
        self.assertEqual(result, os.environ.get("USERNAME"))


if __name__ == "__main__":
    unittest.main()
