import os
import unittest
from .BaseTestCase import BaseTestCase
from ingestor.Template import Template
from ingestor.Template import RequiredPathNotFoundError
from ingestor.Template import VariableNotFoundError
from ingestor.Crawler.Fs import Path

class TemplateTest(BaseTestCase):
    """Test Template crawler."""

    __file = os.path.join(BaseTestCase.dataDirectory(), 'RND-TST-SHT_lighting_beauty_sr.1001.exr')

    def testTemplate(self):
        """
        Test that the Template works properly.
        """
        crawler = Path.createFromPath(self.__file)
        value = '(dirname {filePath})/(newVersion <parentPath>)/{name}.(pad {frame} 6).{ext}'
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
        self.assertEqual(Template('{var}').value(), 'test')


if __name__ == "__main__":
    unittest.main()
