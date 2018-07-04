import json
import sys
from ..Resource import Resource
from ..Crawler.Fs import FsPath
from ..Crawler import Crawler
from ..Template import Template
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

class TaskInvalidOptionValue(Exception):
    """Task invalid option value error."""

class Task(object):
    """
    Abstract Task.

    A task is used to operate over file paths resolved by the template runner.

    Optional options:
        - filterTemplate: This is used when querying the crawlers from the task (Task.pathCrawlers).
        It works by filtering out crawlers based on the template defined as value of the option.
        When the processed template results: "False", "false" or "0" then the crawler is filtered
        out from the pathCrawlers result.

        - emptyFilterResult: This option should be used in combination with
        "filterTemplate" and only works when filterTemplate filters out all crawlers.
        By assigning "taskCrawlers" then the crawlers in the task are returned as result (Similar
        behaviour about what happens in nuke when a node is disabled). Otherwise, when assigned
        with "empty" the task results an empty list (default).
    """

    __registered = {}

    def __init__(self, taskType):
        """
        Create a task object.
        """
        self.__pathCrawlers = OrderedDict()
        self.__metadata = {}
        self.__taskType = taskType
        self.__options = {}

        # default options
        self.setOption('filterTemplate', '')
        self.setOption('emptyFilterResult', 'empty')

        # default metadata
        # taskWrapper is used when executing tasks through a task holder
        self.setMetadata('taskWrapper.name', 'default')
        self.setMetadata('taskWrapper.options', {})

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
            if level not in currentLevel:
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
            currentLevel = currentLevel[level]

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

    def templateOption(self, name, crawler=None, vars={}):
        """
        Return a value resolved by the Template module.
        """
        value = self.option(name)
        if crawler:
            return Template(value).valueFromCrawler(crawler, vars)
        else:
            return Template(value).value(vars)

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

    def pathCrawlers(self, useFilterTemplateOption=True):
        """
        Return a list of path crawlers associated with the task.
        """
        result = list(self.__pathCrawlers.keys())

        # filtering the pathCrawler result based on the "filterTemplate" option
        filterTemplate = str(self.option('filterTemplate'))
        if useFilterTemplateOption and filterTemplate:
            filteredResult = []
            for crawler in result:
                templateResult = Template(filterTemplate).valueFromCrawler(crawler)
                if str(templateResult).lower() not in ['false', '0']:
                    filteredResult.append(crawler)

            result = filteredResult

        return result

    def add(self, pathCrawler, filePath=''):
        """
        Add a path crawler to the task.

        A file path can be associated with the path crawler, this file path may be used
        as target to the path crawler.
        """
        assert isinstance(pathCrawler, FsPath), \
            "Invalid FsPath Crawler!"

        assert isinstance(filePath, basestring), \
            "FilePath needs to be defined as string"

        self.__pathCrawlers[pathCrawler] = filePath

    def clear(self):
        """
        Remove all crawlers associated with the task.
        """
        self.__pathCrawlers.clear()

    def output(self):
        """
        Perform and result a list of crawlers created by task.
        """
        verbose = self.hasMetadata('output.verbose') and self.metadata('output.verbose')
        if verbose:
            sys.stdout.write('{0} output:\n'.format(self.type()))

        # in case all path crawlers were filtered out, returning right away.
        # \TODO: we may want to have the behaviour of don't performing the task
        # when the task does not have any path crawler. Right now, it's only applied
        # when all crawlers were filtered out by the filter template option.
        if len(self.pathCrawlers(useFilterTemplateOption=False)) and len(self.pathCrawlers()) == 0:
            return self.__emptyFilterResult(verbose)

        contextVars = {}
        for crawler in self.pathCrawlers():
            for ctxVarName in crawler.contextVarNames():
                if ctxVarName not in contextVars:
                    contextVars[ctxVarName] = crawler.var(ctxVarName)

        outputCrawlers = self._perform()

        # Copy all context variables to output crawlers
        for outputCrawler in outputCrawlers:
            if verbose:
                sys.stdout.write(
                    '  - {}\n'.format(
                        outputCrawler.var('filePath')
                    )
                )

            for ctxVarName in contextVars:
                outputCrawler.setVar(ctxVarName, contextVars[ctxVarName], True)

        # flushing output stream
        if verbose:
            sys.stdout.flush()

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
            "type": self.type()
        }

        # current metadata
        metadata = self.metadata()

        # current options
        options = {}
        for optionName in self.optionNames():
            options[optionName] = self.option(optionName)

        # crawler data
        crawlerData = []
        for pathCrawler in self.pathCrawlers():
            crawlerData.append({
                'filePath': self.filePath(pathCrawler),
                'serializedCrawler': pathCrawler.toJson()
            })

        # custom resources
        loadedResources = Resource.get().loaded(ignoreFromEnvironment=True)

        # only including them as result if they are not empty
        if len(metadata):
            contents['metadata'] = metadata

        if len(options):
            contents['options'] = options

        if len(crawlerData):
            contents['crawlerData'] = crawlerData

        if len(loadedResources):
            contents['resources'] = loadedResources

        return json.dumps(
            contents,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )

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
        taskOptions = contents.get("options", {})
        taskMetadata = contents.get("metadata", {})
        crawlerData = contents.get("crawlerData", [])
        loadResources = contents.get("resources", [])

        # loading resources
        for loadResource in loadResources:
            if loadResource in Resource.get().loaded():
                continue
            Resource.get().load(loadResource)

        # loading task
        task = Task.create(taskType)

        # setting task options
        for optionName, optionValue in taskOptions.items():
            task.setOption(optionName, optionValue)

        # setting task metadata
        for metadataName, metadataValue in taskMetadata.items():
            task.setMetadata(metadataName, metadataValue)

        # adding crawlers
        for crawlerDataItem in crawlerData:
            filePath = crawlerDataItem['filePath']
            crawler = Crawler.createFromJson(
                crawlerDataItem['serializedCrawler']
            )
            task.add(crawler, filePath)

        return task

    def _perform(self):
        """
        For re-implementation: should implement the computation of the task and return a list of crawlers as output.

        The default implementation return a list of crawlers based on the target filePath (The filePath is provided by
        by the template). In case none file path has not been specified then returns an empty list of crawlers.
        """
        filePaths = []
        for crawler in self.pathCrawlers():
            filePath = self.filePath(crawler)
            if filePath not in filePaths:
                filePaths.append(filePath)

        return list(map(FsPath.createFromPath, filePaths))

    def __emptyFilterResult(self, verbose):
        """
        Auxiliary method to compute an empty filter result.
        """
        if self.option('emptyFilterResult') == 'taskCrawlers':
            if verbose:
                sys.stdout.write('  - Empty filter resulting original task crawlers\n')

            return self.pathCrawlers(useFilterTemplateOption=False)

        elif self.option('emptyFilterResult') == 'empty':
            if verbose:
                sys.stdout.write('  - Empty filter resulting no crawlers\n')

            return []
        else:
            raise TaskInvalidOptionValue(
                'Invalid option value "{}" for "emptyFilterResult"'.format(
                    self.option('emptyFilterResult')
                )
            )
