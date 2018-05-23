from .Template import Template
from .PathCrawlerMatcher import PathCrawlerMatcher
from collections import OrderedDict

class PathCrawlerQuery(object):
    """
    Query the path crawlers that meet the specification.
    """

    def __init__(self, template, pathCrawlerMatcher):
        """
        Create a template resolver object.
        """
        self.__setTemplate(template)
        self.__setPathCrawlerMatcher(pathCrawlerMatcher)

    def template(self):
        """
        Return the template.
        """
        return self.__template

    def pathCrawlerMatcher(self):
        """
        Return the crawler path matcher that defines the specification.
        """
        return self.__pathCrawlerMatcher

    def query(self, pathCrawlers, vars={}):
        """
        Return a dict containg the matched crawler as key and resolved template as value.
        """
        validPathCrawlers = {}
        for pathCrawler in pathCrawlers:
            if self.pathCrawlerMatcher().match(pathCrawler):
                templateValue = self.template().valueFromCrawler(pathCrawler, vars)
                validPathCrawlers[pathCrawler] = templateValue

        # sorting result
        result = OrderedDict()
        for pathCrawler, filePath in sorted(validPathCrawlers.items(), key=lambda x: x[1] + '|' + x[0].var('filePath')):
            result[pathCrawler] = filePath

        return result

    def __setTemplate(self, template):
        """
        Set a template to the runner.
        """
        assert isinstance(template, Template), \
            "Invalid template type!"

        self.__template = template

    def __setPathCrawlerMatcher(self, pathCrawlerMatcher):
        """
        Set a path crawler matcher.
        """
        assert isinstance(pathCrawlerMatcher, PathCrawlerMatcher), \
            "Invalid path crawler matcher type!"

        self.__pathCrawlerMatcher = pathCrawlerMatcher
