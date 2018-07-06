from .Template import Template
from .CrawlerMatcher import CrawlerMatcher
from collections import OrderedDict

class CrawlerQuery(object):
    """
    Query the crawlers that meet the specification.
    """

    def __init__(self, template, crawlerMatcher):
        """
        Create a template resolver object.
        """
        self.__setTemplate(template)
        self.__setCrawlerMatcher(crawlerMatcher)

    def template(self):
        """
        Return the template.
        """
        return self.__template

    def crawlerMatcher(self):
        """
        Return the crawler path matcher that defines the specification.
        """
        return self.__crawlerMatcher

    def query(self, crawlers, vars={}):
        """
        Return a dict containg the matched crawler as key and resolved template as value.
        """
        validCrawlers = {}
        for crawler in crawlers:
            if self.crawlerMatcher().match(crawler):
                templateValue = self.template().valueFromCrawler(crawler, vars)
                validCrawlers[crawler] = templateValue

        # sorting result
        result = OrderedDict()
        for crawler, filePath in sorted(validCrawlers.items(), key=lambda x: x[1] + '|' + x[0].var('filePath')):
            result[crawler] = filePath

        return result

    def __setTemplate(self, template):
        """
        Set a template to the runner.
        """
        assert isinstance(template, Template), \
            "Invalid template type!"

        self.__template = template

    def __setCrawlerMatcher(self, crawlerMatcher):
        """
        Set a crawler matcher.
        """
        assert isinstance(crawlerMatcher, CrawlerMatcher), \
            "Invalid crawler matcher type!"

        self.__crawlerMatcher = crawlerMatcher
