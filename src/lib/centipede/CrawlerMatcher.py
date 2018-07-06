from fnmatch import fnmatch
from .Crawler import Crawler

class CrawlerMatcher(object):
    """
    Used to check if a crawler meets the specification of the matcher.
    """

    def __init__(self, matchTypes=[], matchVars={}):
        """
        Create a crawler matcher object.
        """
        self.__setMatchTypes(matchTypes)
        self.__setMatchVars(matchVars)

    def matchTypes(self):
        """
        Return a list of crawler types used to match.
        """
        return self.__matchTypes

    def matchVarNames(self):
        """
        Return a list of variable names that should be used to match the crawler.
        """
        return self.__matchVars.keys()

    def matchVar(self, varName):
        """
        Return the variable value.
        """
        return self.__matchVars[varName]

    def match(self, crawler):
        """
        Return a boolean telling if the crawler matches.

        TODO: ideally it should be breakdown in two methods, so one that
        test and another one that actually throwns an exception telling
        why it does not match.
        """
        assert isinstance(crawler, Crawler), \
            "Invalid crawler type!"

        crawlerType = crawler.var('type')
        foundType = not self.matchTypes()
        for matchType in self.matchTypes():
            registeredTypes = Crawler.registeredSubTypes(matchType)
            if crawlerType in registeredTypes:
                foundType = True
                break

        if not foundType:
            return False

        for varName in self.matchVarNames():

            # checking if variable is part of the crawler
            if varName not in crawler.varNames():
                return False

            matchVarValue = self.matchVar(varName)

            # the value can be a list of possibiblities
            if not isinstance(matchVarValue, list):
                matchVarValue = [matchVarValue]

            foundValueValue = False
            for value in matchVarValue:
                if fnmatch(str(crawler.var(varName)), str(value)):
                    foundValueValue = True
                    break

            if not foundValueValue:
                return False

        return True

    def __setMatchTypes(self, matchTypes):
        """
        Set a list of crawler types used to match.

        The types can be defined using glob syntax.
        """
        assert isinstance(matchTypes, list), \
            "Invalid list!"

        self.__matchTypes = list(matchTypes)

    def __setMatchVars(self, matchVars):
        """
        Set a list of variable names that should match in the crawler.

        The var values can be defined using glob syntax.
        """
        assert isinstance(matchVars, dict), \
            "Invalid dict!"

        self.__matchVars = dict(matchVars)
