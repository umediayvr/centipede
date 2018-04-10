import os
from collections import OrderedDict

class InvalidVarError(Exception):
    """Invalid Var Error."""

class InvalidTagError(Exception):
    """Invalid Tag Error."""

class Crawler(object):
    """
    Abstracted Crawler.
    """

    def __init__(self, name, parentCrawler=None):
        """
        Create a crawler.
        """
        self.__vars = {}
        self.__contextVarNames = set()
        self.__tags = {}
        self.__hasComputedSelf = False

        # passing variables
        if parentCrawler:
            assert isinstance(parentCrawler, Crawler), \
                "Invalid crawler type!"

            for varName in parentCrawler.varNames():
                isContextVar = (varName in parentCrawler.contextVarNames())
                self.setVar(varName, parentCrawler.var(varName), isContextVar)

            self.setVar(
                'path',
                os.path.join(
                    parentCrawler.var('path'),
                    name
                )
            )
        else:
            self.setVar('path', '/')

        self.setVar('name', name)

    def isLeaf(self):
        """
        For re-implementation: Return a boolean telling if the crawler is leaf.
        """
        return True

    def children(self):
        """
        Return a list of crawlers.
        """
        assert not self.isLeaf(), "Can't compute children from a leaf crawler!"

        result = self._computeChildren()
        for crawler in result:
            assert isinstance(crawler, Crawler), \
                "Invalid Crawler Type"

        return result

    def varNames(self):
        """
        Return a list of variable names assigned to the crawler.
        """
        return list(self.__vars.keys())

    def contextVarNames(self):
        """
        Return a list of variable names that are defined as context variables.
        """
        return list(self.__contextVarNames)

    def setVar(self, name, value, isContextVar=False):
        """
        Set a value for a variable.
        """
        if isContextVar:
            self.__contextVarNames.add(name)
        self.__vars[name] = value

    def var(self, name):
        """
        Return the value for a variable.
        """
        if name not in self.__vars:
            raise InvalidVarError(
                'Variable not found "{0}"'.format(name)
            )

        return self.__vars[name]

    def tagNames(self):
        """
        Return a list of tag names assigned to the crawler.
        """
        return self.__tags.keys()

    def setTag(self, name, value):
        """
        Set a value for a tag.
        """
        self.__tags[name] = value

    def tag(self, name):
        """
        Return the value for a tagiable.
        """
        if name not in self.__tags:
            raise InvalidTagError(
                'Tag not found "{0}"'.format(name)
            )

        return self.__tags[name]

    def clone(self):
        """
        For re-implementation: Should return a cloned instance of the current crawler.
        """
        raise NotImplementedError

    @staticmethod
    def group(crawlers, tag='group'):
        """
        Return the crawlers grouped by the input tag.

        The result is a 2D array where each group of the result is a list of crawlers
        that contain the same tag value. The crawlers inside of the group are
        sorted alphabetically using the path by default. If you want to do a custom
        sorting, take a look at: Crawler.sortGroup
        """
        groupedCrawlers = OrderedDict()
        uniqueCrawlers = []
        for crawler in crawlers:
            if tag in crawler.tagNames():
                groupName = crawler.tag(tag)
                if groupName not in groupedCrawlers:
                    groupedCrawlers[groupName] = []
                groupedCrawlers[groupName].append(crawler)
            else:
                uniqueCrawlers.append([crawler])

        # sorting crawlers
        groupedSorted = Crawler.sortGroup(
            groupedCrawlers.values(),
            key=lambda x: x.var('path')
        )

        return groupedSorted + uniqueCrawlers

    @staticmethod
    def sortGroup(crawlers, key=None, reverse=False):
        """
        Return a list of grouped crawlers sorted by the input key.
        """
        result = []
        for group in crawlers:
            result.append(list(sorted(group, key=key, reverse=reverse)))
        return result
