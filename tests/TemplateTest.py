import os
import unittest
from .BaseTestCase import BaseTestCase
from centipede.Template import Template
from centipede.Template import RequiredPathNotFoundError
from centipede.Template import VariableNotFoundError
from centipede.Crawler.Fs import FsPath

class TemplateTest(BaseTestCase):
    """Test Template crawler."""

    __file = os.path.join(BaseTestCase.dataDirectory(), 'RND-TST-SHT_lighting_beauty_sr.1001.exr')

    def testTemplate(self):
        """
        Test that the Template works properly.
        """
        crawler = FsPath.createFromPath(self.__file)
        value = '(dirname {filePath})/(newver <parentPath>)/{name}.(pad {frame} 6).{ext}'
        result = Template(value).valueFromCrawler(crawler)
        self.assertEqual(result, os.path.join(
                BaseTestCase.dataDirectory(),
                'v003',
                'RND-TST-SHT_lighting_beauty_sr.001001.exr')
                )

    def testTemplateRequiredPath(self):
        """
        Test that the required path check works.
        """
        value = '{}/!badPath/test.exr'.format(BaseTestCase.dataDirectory())
        self.assertRaises(RequiredPathNotFoundError, Template(value).value)
        value = '{}/!glob'.format(BaseTestCase.dataDirectory())
        result = Template(value).value()
        self.assertEqual(result, os.path.join(BaseTestCase.dataDirectory(), 'glob'))

    def testTemplateVariable(self):
        """
        Test that you can pass variables to the template properly.
        """
        variables = {'otherVar': 'value'}
        self.assertRaises(VariableNotFoundError, Template('{var}').value, variables)
        variables['var'] = 'test'
        self.assertEqual(Template('{var}').value(variables), 'test')


if __name__ == "__main__":
    unittest.main()
