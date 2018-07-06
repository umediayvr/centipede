import unittest
import os
from ...BaseTestCase import BaseTestCase
from centipede.Task import Task
from centipede.Crawler.Fs import FsPath
from centipede.Task.Fs.Checksum import ChecksumMatchError
from centipede.Task.Image import UpdateImageMetadata

class UpdateImageMetadataTest(BaseTestCase):
    """Test UpdateImageMetadata task."""

    __sourcePath = os.path.join(BaseTestCase.dataDirectory(), "test.exr")
    __targetPath = os.path.join(BaseTestCase.dataDirectory(), "testToDelete.exr")

    def testUpdateImageMetadata(self):
        """
        Test that the UpdateImageMetadata task works properly.
        """
        crawler = FsPath.createFromPath(self.__sourcePath)
        updateTask = Task.create('updateImageMetadata')
        updateTask.add(crawler, self.__targetPath)
        result = updateTask.output()
        self.assertEqual(len(result), 1)
        crawler = result[0]

        import OpenImageIO as oiio
        inputSpec = oiio.ImageInput.open(self.__targetPath).spec()
        self.assertEqual(inputSpec.get_string_attribute("centipede:sourceFile"), self.__sourcePath)
        self.assertEqual(inputSpec.get_string_attribute("centipede:centipedeUser"), os.environ['USERNAME'])
        checkTask = Task.create('checksum')
        checkTask.add(crawler, self.__sourcePath)
        self.assertRaises(ChecksumMatchError, checkTask.output)

        customMetadata = {"testInt": 0, "testStr": "True"}
        UpdateImageMetadata.updateDefaultMetadata(inputSpec, crawler, customMetadata)
        self.assertEqual(inputSpec.get_int_attribute("centipede:testInt"), 0)
        self.assertEqual(inputSpec.get_string_attribute("centipede:testStr"), "True")

    @classmethod
    def tearDownClass(cls):
        """
        Remove the file that was created.
        """
        os.remove(cls.__targetPath)


if __name__ == "__main__":
    unittest.main()
