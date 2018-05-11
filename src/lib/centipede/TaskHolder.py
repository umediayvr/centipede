import json
from .Task import Task
from .TaskWrapper import TaskWrapper
from .Template import Template
from .PathCrawlerMatcher import PathCrawlerMatcher
from .PathCrawlerQuery import PathCrawlerQuery

class TaskHolderInvalidVarNameError(Exception):
    """Task holder invalid var name error."""

class TaskHolder(object):
    """
    Holds task and sub task holders associated with a target template and path crawler matcher.
    """

    def __init__(self, task, targetTemplate=None, pathCrawlerMatcher=None):
        """
        Create a task holder object.
        """
        self.setTask(task)

        if targetTemplate is None:
            targetTemplate = Template()
        self.__setTargetTemplate(targetTemplate)

        if pathCrawlerMatcher is None:
            pathCrawlerMatcher = PathCrawlerMatcher()
        self.__setPathCrawlerMatcher(pathCrawlerMatcher)

        self.__subTaskHolders = []
        self.__contextVarNames = set()
        self.__taskWrapper = TaskWrapper.create('default')
        self.__vars = {}
        self.__query = PathCrawlerQuery(
            self.targetTemplate(),
            self.pathCrawlerMatcher()
        )

    def addVar(self, name, value, isContextVar=False):
        """
        Add a variable to the task holder.
        """
        if isContextVar:
            self.__contextVarNames.add(name)
        elif name in self.__contextVarNames:
            self.__contextVarNames.remove(name)

        self.__vars[name] = value

    def varNames(self):
        """
        Return a list of variable names.
        """
        return self.__vars.keys()

    def var(self, name):
        """
        Return the value for the variable.
        """
        if name not in self.__vars:
            raise TaskHolderInvalidVarNameError(
                'Invalid variable name "{0}'.format(
                    name
                )
            )

        return self.__vars[name]

    def contextVarNames(self):
        """
        Return a list of variable names defined as context variables.
        """
        return list(self.__contextVarNames)

    def setTaskWrapper(self, taskWrapper):
        """
        Override the default task wrapper.
        """
        assert isinstance(taskWrapper, TaskWrapper), "Invalid taskWrapper type!"

        self.__taskWrapper = taskWrapper

    def taskWrapper(self):
        """
        Return the task wrapper used to execute the task.
        """
        return self.__taskWrapper

    def targetTemplate(self):
        """
        Return the targetTemplate associated with the task holder.
        """
        return self.__targetTemplate

    def setTask(self, task):
        """
        Associate a cloned task with the task holder.
        """
        assert isinstance(task, Task), \
            "Invalid Task type"

        self.__task = task.clone()

    def task(self):
        """
        Return the task associted with the task holder.
        """
        return self.__task

    def addPathCrawlers(self, crawlers, addTaskHolderVars=True):
        """
        Add a list of crawlers to the task.

        The crawlers are added to the task using "query" method to resolve
        the target template.
        """
        for crawler, filePath in self.query(crawlers).items():

            if addTaskHolderVars:
                # cloning crawler so we can modify it safely
                crawler = crawler.clone()

                for varName in self.varNames():
                    crawler.setVar(
                        varName,
                        self.var(varName),
                        varName in self.contextVarNames()
                    )

            self.__task.add(
                crawler,
                filePath
            )

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
        return list(self.__subTaskHolders)

    def cleanSubTaskHolders(self):
        """
        Remove all sub task holders from the current task holder.
        """
        del self.__subTaskHolders[:]

    def query(self, pathCrawlers):
        """
        Query path crawlers that meet the specification.
        """
        return self.__query.query(
            pathCrawlers,
            self.__vars
        )

    def toJson(self, includeSubTaskHolders=True):
        """
        Bake the current task holder (including all sub task holders) to json.
        """
        return json.dumps(
            self.__bakeTaskHolder(self, includeSubTaskHolders),
            indent=4,
            separators=(',', ': ')
        )

    def clone(self, includeSubTaskHolders=True):
        """
        Return a cloned instance of the current task holder.
        """
        return self.createFromJson(self.toJson(includeSubTaskHolders))

    def run(self, crawlers=[]):
        """
        Perform the task.

        Return all the crawlers resulted by the execution of the task (and sub tasks).
        """
        return self.__recursiveTaskRunner(
            self,
            crawlers
        )

    @classmethod
    def createFromJson(cls, jsonContents):
        """
        Create a new task holder instance from json.
        """
        contents = json.loads(jsonContents)

        return cls.__loadTaskHolder(contents)

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
    def __bakeTaskHolder(cls, taskHolder, includeSubTaskHolders=True):
        """
        Auxiliary method to bake the task holder recursively.
        """
        # template info
        targetTemplate = taskHolder.targetTemplate().inputString()
        vars = {}
        for varName in taskHolder.varNames():
            vars[varName] = taskHolder.var(varName)

        # path crawler matcher info
        matchTypes = taskHolder.pathCrawlerMatcher().matchTypes()
        matchVars = {}
        for matchVarName in taskHolder.pathCrawlerMatcher().matchVarNames():
            matchVars[matchVarName] = taskHolder.pathCrawlerMatcher().matchVar(matchVarName)

        # task wrapper info
        taskWrapperType = taskHolder.taskWrapper().type()
        taskWrapperOptions = {}
        for optionName in taskHolder.taskWrapper().optionNames():
            taskWrapperOptions[optionName] = taskHolder.taskWrapper().option(optionName)

        output = {
            'template': {
                'target': targetTemplate
            },
            'patchCrawlerMatcher': {
                'matchTypes': matchTypes,
                'matchVars': matchVars
            },
            'vars': vars,
            'contextVarNames': taskHolder.contextVarNames(),
            'task': taskHolder.task().toJson(),
            'taskWrapper': {
                'type': taskWrapperType,
                'options': taskWrapperOptions
            },
            'subTaskHolders': []
        }

        if includeSubTaskHolders:
            output['subTaskHolders'] = list(map(cls.__bakeTaskHolder, taskHolder.subTaskHolders()))

        return output

    @classmethod
    def __loadTaskHolder(cls, taskHolderContents):
        """
        Auxiliary method used to load the contents of the task holder recursively.
        """
        # creating task holder
        template = Template(taskHolderContents['template']['target'])
        pathCrawlerMatcher = PathCrawlerMatcher(
            taskHolderContents['patchCrawlerMatcher']['matchTypes'],
            taskHolderContents['patchCrawlerMatcher']['matchVars']
        )

        # creating task
        task = Task.createFromJson(taskHolderContents['task'])

        # building the task holder instance
        taskHolder = TaskHolder(
            task,
            template,
            pathCrawlerMatcher
        )

        # creating task wrapper
        taskWrapper = TaskWrapper.create(taskHolderContents['taskWrapper']['type'])
        for optionName, optionValue in taskHolderContents['taskWrapper']['options'].items():
            taskWrapper.setOption(optionName, optionValue)
        taskHolder.setTaskWrapper(taskWrapper)

        # adding vars
        contextVarNames = taskHolderContents['contextVarNames']
        for varName, varValue in taskHolderContents['vars'].items():
            taskHolder.addVar(
                varName,
                varValue,
                varName in contextVarNames
            )

        # adding sub task holders
        for subTaskHolderContent in taskHolderContents['subTaskHolders']:
            taskHolder.addSubTaskHolder(cls.__loadTaskHolder(subTaskHolderContent))

        return taskHolder

    @classmethod
    def __recursiveTaskRunner(cls, taskHolder, crawlers):
        """
        Perform the task runner recursively.
        """
        result = []
        taskHolder.addPathCrawlers(crawlers)

        # in case the task does not have any path crawlers, there is nothing to do
        if not taskHolder.task().pathCrawlers():
            return result

        # executing task through the wrapper
        taskCrawlers = taskHolder.taskWrapper().run(taskHolder.task())
        result += taskCrawlers

        # calling subtask holders
        for subTaskHolder in taskHolder.subTaskHolders():
            result += cls.__recursiveTaskRunner(subTaskHolder, taskCrawlers)

        return result
