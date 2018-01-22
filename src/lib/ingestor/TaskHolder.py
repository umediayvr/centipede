import sys
from .Task import Task
from .TaskWrapper import TaskWrapper
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
        self.__taskWrapper = TaskWrapper.create('default')
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

    def customVar(self, name):
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

    def setTaskWrapper(self, taskWrapper):
        """
        Override the default task wrapper to use a custom one.
        """
        assert isinstance(taskWrapper, TaskWrapper), "Invalid taskWrapper type!"

        self.__taskWrapper = taskWrapper

    def taskWrapper(self):
        """
        Return the task wrapper used to execute the task.
        """
        return self.__taskWrapper

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

    def run(self, crawlers, verbose=True):
        """
        Perform the task.
        """
        # running task per group
        groupedCrawlers = {}
        noGroupIndex = 0
        for crawler in crawlers:
            # group
            if 'group' in crawler.tagNames():
                groupName = str(crawler.tag('group'))
                if groupName not in groupedCrawlers:
                    groupedCrawlers[groupName] = []

                groupedCrawlers[groupName].append(crawler)

            # no group
            else:
                groupedCrawlers[noGroupIndex] = [crawler]
                noGroupIndex += 1

        for crawlers in groupedCrawlers.values():
            self.__recursiveTaskRunner(crawlers, self, verbose)

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

    @classmethod
    def __recursiveTaskRunner(cls, crawlers, taskHolder, verbose):
        """
        Perform the task runner recursively.
        """
        matchedCrawlers = taskHolder.query(crawlers)
        if not matchedCrawlers:
            return

        # cloning task so we can modify it safely
        clonedTask = taskHolder.task().clone()
        clonedCrawlers = {}
        for matchedCrawler, targetFilePath in matchedCrawlers.items():

            # cloning crawler so we can modify it safely
            clonedCrawler = matchedCrawler.clone()
            clonedCrawlers[clonedCrawler] = targetFilePath

            # passing custom variables from the task holder to the crawlers.
            # This basically transfer the global variables declared in
            # the json configuration to the crawler, so subtasks can use
            # them to resolve templates (when necessary).
            for customVarName in taskHolder.customVarNames():
                clonedCrawler.setVar(
                    customVarName,
                    taskHolder.customVar(customVarName)
                )

            clonedTask.add(clonedCrawler, targetFilePath)

        # performing task
        currentTaskName = type(clonedTask).__name__

        if verbose:
            sys.stdout.write('Running task: {0}\n'.format(currentTaskName))

        # executing task through the wrapper
        resultCrawlers = taskHolder.taskWrapper().run(clonedTask)
        for pathCrawler in resultCrawlers:
            if verbose:
                sys.stdout.write('  - {0}: {1}\n'.format(
                        currentTaskName,
                        pathCrawler.var('filePath'),
                    )
                )
                sys.stdout.flush()
                sys.stderr.flush()

        # calling subtask holders
        for subTaskHolder in taskHolder.subTaskHolders():
            cls.__recursiveTaskRunner(resultCrawlers, subTaskHolder, verbose)
