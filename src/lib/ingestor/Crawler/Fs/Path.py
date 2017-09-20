import os
from ..Crawler import Crawler
from ...PathHolder import PathHolder
from collections import OrderedDict

class InvalidPathError(Exception):
    """Invalid Path Error."""

class InvalidCrawlerTypeError(Exception):
    """Invalid Crawler Type Error."""

class Path(Crawler):
    """
    Abstracted Path.
    """

    __registeredTypes = OrderedDict()

    def __init__(self, pathHolder, parentCrawler=None):
        """
        Create a crawler (use the factory function Path.create instead).
        """
        super(Path, self).__init__(pathHolder.baseName(), parentCrawler)

        self.__setPathHolder(pathHolder)
        self.setVar('filePath', pathHolder.path())
        self.setVar('ext', pathHolder.ext())
        self.setVar('baseName', pathHolder.baseName())
        self.setVar('name', os.path.splitext(pathHolder.baseName())[0])

    def pathHolder(self):
        """
        Return the path holder object used to create the crawler.
        """
        return self.__pathHolder

    @classmethod
    def test(cls, parentCrawler, pathInfo):
        """
        Tells if crawler implementation, can handle it.

        For re-implementation: Should return a bollean telling if the
        crawler implementation can crawler it.
        """
        raise NotImplemented

    @staticmethod
    def register(name, crawlerClass):
        """
        Register a path type.

        The registration is used to tell the order that the crawler types
        are going to be tested. The test is done from the latest registrations to
        the first registrations (bottom top). The only exception is for types that
        get overriden where the position is going to be the same.
        """
        assert issubclass(crawlerClass, Path), \
            "Invalid crawler class!"

        Path.__registeredTypes[name] = crawlerClass

    @staticmethod
    def registeredNames():
        """
        Return a list of registered path types.
        """
        return Path.__registeredTypes.keys()

    @staticmethod
    def create(pathHolder, parentCrawler=None):
        """
        Create a crawler for the input path holder.
        """
        result = None
        for registeredName in reversed(Path.__registeredTypes.keys()):
            testCrawlerType = Path.__registeredTypes[registeredName]
            if testCrawlerType.test(pathHolder, parentCrawler):
                result = testCrawlerType(pathHolder, parentCrawler)
                result.setVar('type', registeredName)
                break

        assert result, \
            "Don't know how to create a path crawler for \"{0}\"".format(
                pathHolder.path()
            )
        return result

    def __setPathHolder(self, pathHolder):
        """
        Set the path holder to the crawler.
        """
        assert isinstance(pathHolder, PathHolder), \
            "Invalid PathHolder type"

        self.__pathHolder = pathHolder
