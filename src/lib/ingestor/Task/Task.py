import os
import json
from ..Crawler.Fs import Path
from collections import OrderedDict

# compatibility with python 2/3
try:
    basestring
except NameError:
    basestring = str

class TaskTypeNotFoundError(Exception):
    """Task type not found error."""

class InvalidPathCrawlerError(Exception):
    """Invalid path crawler Error."""

class TaskInvalidOptionError(Exception):
    """Task invalid option error."""

class TaskInvalidMetadataError(Exception):
    """Task invalid metadata error."""

class Task(object):
    """
    Abstract Task.

    A task is used to operate over file paths resolved by the template runner.
    """

    __registered = {}

    def __init__(self, taskType):
        """
        Create a task object.
        """
        self.__pathCrawlers = OrderedDict()
        self.__options = {}
        self.__metadata = {}
        self.__taskType = taskType

    def type(self):
        """
        Return the task type.
        """
        return self.__taskType

    def metadata(self, scope=''):
        """
        Return the metadata.

        The metadata is represented as dictionary. You can query the entire
        metadata by passing an empty string as scope (default). Otherwise,
        you can pass a scope string separating each level by '.' (for instance:
        fisrt.second.third).
        """
        if not scope:
            return self.__metadata

        currentLevel = self.__metadata
        for level in scope.split('.'):
            if not level in currentLevel:
                raise TaskInvalidMetadataError(
                    'Invalid metadata "{}"'.format(scope)
                )

            currentLevel = currentLevel[level]

        return currentLevel

    def setMetadata(self, scope, value):
        """
        Set an arbitrary metadata.

        In case you want to set a multi-dimension value under the metadata,
        you can you the scope for it by passing the levels separated by "."
        (The levels are created automatically as new dictonaries in case they
        don't exist yet). Make sure the data being set inside of the metadata
        can be serialized through json.
        """
        assert scope, "scope cannot be empty"

        # we want to store an immutable value under the metadata
        safeValue = json.loads(json.dumps(value))

        # creating auxiliary levels
        levels = scope.split('.')
        currentLevel = self.__metadata
        for level in levels[:-1]:
            if level not in currentLevel:
                currentLevel[level] = {}

            currentLevel = currentLevel[level]

        currentLevel[levels[-1]] = safeValue

    def metadataNames(self):
        """
        Return a list with the names of the root levels under the metadata.
        """
        return list(self.__metadata.keys())

    def hasMetadata(self, scope):
        """
        Return a boolean telling if the input scope is under the metadata.

        In case the scope is empty, then the result is done based if there's
        any information under the metadata.
        """
        if not scope:
            return bool(len(self.__metadata))

        levels = scope.split('.')
        currentLevel = self.__metadata
        found = True
        for level in levels[:-1]:
            if level not in currentLevel:
                found = False
                break

        if found and levels[-1] in currentLevel:
            return True

        return False

    def option(self, name):
        """
        Return a value for an option.
        """
        if name not in self.__options:
            raise TaskInvalidOptionError(
                'Invalid option name: "{0}"'.format(
                    name
                )
            )

        return self.__options[name]

    def setOption(self, name, value):
        """
        Set an option to the task.
        """
        self.__options[name] = value

    def optionNames(self):
        """
        Return a list of the option names.
        """
        return list(self.__options.keys())

    def filePath(self, pathCrawler):
        """
        Return the file path for path crawler.
        """
        if pathCrawler not in self.__pathCrawlers:
            raise InvalidPathCrawlerError(
                'Path crawler is not part of the task!'
            )

        return self.__pathCrawlers[pathCrawler]

    def pathCrawlers(self):
        """
        Return a list of path crawlers associated with the task.
        """
        return list(self.__pathCrawlers.keys())

    def add(self, pathCrawler, filePath=''):
        """
        Add a file path associate with a path crawler to the Task.
        """
        assert isinstance(pathCrawler, Path), \
            "Invalid Path Crawler!"

        assert isinstance(filePath, basestring), \
            "FilePath needs to be defined as string"

        self.__pathCrawlers[pathCrawler] = filePath

    def output(self):
        """
        Perform and result a list of crawlers created by task.
        """
        contextVars = {}
        for crawler in self.pathCrawlers():
            for ctxVarName in crawler.contextVarNames():
                if ctxVarName not in contextVars:
                    contextVars[ctxVarName] = crawler.var(ctxVarName)

        outputCrawlers = self._perform()

        # Copy all context variables to output crawlers
        for outputCrawler in outputCrawlers:
            for ctxVarName in contextVars:
                outputCrawler.setVar(ctxVarName, contextVars[ctxVarName], True)

        return outputCrawlers

    def clone(self):
        """
        Clone the current task.
        """
        clone = self.__class__(self.type())

        # copying options
        for optionName in self.optionNames():
            clone.setOption(optionName, self.option(optionName))

        # copying metadata
        for metadataName in self.metadataNames():
            clone.setMetadata(metadataName, self.metadata(metadataName))

        # copying path crawlers
        for pathCrawler in self.pathCrawlers():
            clone.add(pathCrawler, self.filePath(pathCrawler))

        return clone

    def toJson(self):
        """
        Serialize a task to json (it can be loaded later through createFromJson).
        """
        contents = {
            "type": self.type(),
            "options": {},
            "metadata": self.metadata(),
            "jsonConfigPath": "",
            "configName": "",
            "pathCrawlerData": []
        }

        # current options
        for optionName in self.optionNames():
            contents["options"][optionName] = self.option(optionName)

        for pathCrawler in self.pathCrawlers():

            # we can expect all crawlers in the task to have the same configPath
            # and configName (when defined)
            if not contents['jsonConfigPath'] and 'configName' in pathCrawler.varNames():
                contents['jsonConfigPath'] = os.path.join(
                    pathCrawler.var("configPath"),
                    pathCrawler.var("configName")
                )

            contents['pathCrawlerData'].append({
                'filePath': self.filePath(pathCrawler),
                'serializedPathCrawler': pathCrawler.toJson()
            })

        return json.dumps(contents)

    @staticmethod
    def register(name, taskClass):
        """
        Register a task type.
        """
        assert issubclass(taskClass, Task), \
            "Invalid task class!"

        Task.__registered[name] = taskClass

    @staticmethod
    def registeredNames():
        """
        Return a list of registered tasks.
        """
        return list(Task.__registered.keys())

    @staticmethod
    def create(taskType, *args, **kwargs):
        """
        Create a task object.
        """
        if taskType not in Task.__registered:
            raise TaskTypeNotFoundError(
                'Task name is not registed: "{0}"'.format(
                    taskType
                )
            )
        return Task.__registered[taskType](taskType, *args, **kwargs)

    @staticmethod
    def createFromJson(jsonContents):
        """
        Create a task based on the jsonContents (serialized via toJson).
        """
        contents = json.loads(jsonContents)
        taskType = contents["type"]
        taskOptions = contents["options"]
        taskMetadata = contents["metadata"]
        pathCrawlerData = contents["pathCrawlerData"]
        jsonConfigPath = contents["jsonConfigPath"]

        # loading json config which may load custom crawlers, expressions etc...
        if jsonConfigPath:
            from ..TaskHolderLoader import JsonLoader
            JsonLoader().addFromJsonFile(jsonConfigPath)

        task = Task.create(taskType)

        # setting task options
        for optionName, optionValue in taskOptions.items():
            task.setOption(optionName, optionValue)

        # setting task metadata
        for metadataName, metadataValue in taskMetadata.items():
            task.setMetadata(metadataName, metadataValue)

        # adding crawlers
        for pathCrawlerDataItem in pathCrawlerData:
            filePath = pathCrawlerDataItem['filePath']
            crawler = Path.createFromJson(
                pathCrawlerDataItem['serializedPathCrawler']
            )
            task.add(crawler, filePath)

        return task

    def _perform(self):
        """
        For re-implementation: should implement the computation of the task and return a list of crawlers as output.

        The default implementation return a list of crawlers based on the target filePath (The filePath is provided by
        by the template). In case none file path has not been specified then returns an empty list of crawlers.
        """
        filePaths = set()
        for crawler in self.pathCrawlers():
            filePath = self.filePath(crawler)
            if filePath:
                filePaths.add(filePath)

        return list(map(Path.createFromPath, filePaths))
