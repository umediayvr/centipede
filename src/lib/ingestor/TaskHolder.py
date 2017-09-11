from .Task import Task
from .Template import Template
from .PathCrawlerMatcher import PathCrawlerMatcher
from .PathCrawlerQuery import PathCrawlerQuery

class InvalidCustomVariableNameError(Exception):
    """Invalid custom variable name error."""

class TaskHolder(object):
    """
    Holds task and subtasks associated with a target template and path crawler matcher.
    """

    def __init__(self, task, targetTemplate, pathCrawlerMatcher):
        """
        Create a task holder object.
        """
        self.__setTask(task)
        self.__setTargetTemplate(targetTemplate)
        self.__setPathCrawlerMatcher(pathCrawlerMatcher)
        self.__subTaskHolders = []
        self.__vars = {}
        self.__query = PathCrawlerQuery(
            self.targetTemplate(),
            self.pathCrawlerMatcher()
        )

    def addCustomVar(self, name, value):
        """
        Add a variable that is going to be passed later to the query.
        """
        self.__vars[name] = value

    def customVarNames(self):
        """
        Return a list of custom variable names that are passed to the query.
        """
        return self.__vars.keys()

    def varValue(name):
        """
        Return the value for the variable name.
        """
        if name not in self.__vars:
            raise InvalidCustomVariableNameError(
                'Invalid variable name "{0}'.format(
                    name
                )
            )

        return self.__vars[name]

    def task(self):
        """
        Return the task associted with the task holder.
        """
        return self.__task

    def targetTemplate(self):
        """
        Return the targetTemplate associated with the task holder.
        """
        return self.__targetTemplate

    def pathCrawlerMatcher(self):
        """
        Return the path crawler matcher associated with the task holder.
        """
        return self.__pathCrawlerMatcher

    def addSubTaskHolder(self, taskHolder):
        """
        Add a subtask holder with the current holder.
        """
        assert isinstance(taskHolder, TaskHolder), \
            "Invalid Task Holder Type"

        self.__subTaskHolders.append(taskHolder)

    def subTaskHolders(self):
        """
        Return a list sub task holders associated with the task holder.
        """
        return self.__subTaskHolders

    def query(self, pathCrawlers):
        """
        Query path crawlers that meet the specification.
        """
        return self.__query.query(pathCrawlers, self.__vars)

    def __setTask(self, task):
        """
        Associate a task with the task holder.
        """
        assert isinstance(task, Task), \
            "Invalid Task type"

        self.__task = task

    def __setTargetTemplate(self, targetTemplate):
        """
        Associate a target template with the task holder.
        """
        assert isinstance(targetTemplate, Template), \
            "Invalid template type"

        self.__targetTemplate = targetTemplate

    def __setPathCrawlerMatcher(self, pathCrawlerMatcher):
        """
        Associate a path crawler matcher with the task holder.
        """
        assert isinstance(pathCrawlerMatcher, PathCrawlerMatcher), \
            "Invalid PathCrawlerMatcher type"
        self.__pathCrawlerMatcher = pathCrawlerMatcher
