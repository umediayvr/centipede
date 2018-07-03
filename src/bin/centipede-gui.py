import os
import re
import sys
import json
import datetime
import functools
import subprocess
import centipede
from centipede.Dispatcher import Dispatcher
from centipede.Crawler import Crawler
from collections import OrderedDict
from PySide2 import QtCore, QtGui, QtWidgets

class CentipedeApp(QtWidgets.QApplication):
    """
    Basic graphical interface to pick files to run through a centipede configuration.

    Deprecation Notice: This interface is going to be phase out in future releases.

    Example:
        centipede <CONFIGURATION-DIRECTORY> [<INPUT-FILES-DIRECTORY>]
    """

    __viewModes = ["group", "flat"]
    __runOnTheFarm = os.environ.get('CENTIPEDEAPP_RUN_FARM', '0')

    def __init__(self, argv, **kwargs):
        """
        Create a Centipede app.
        """
        super(CentipedeApp, self).__init__(argv, **kwargs)

        self.__configurationDirectory = ""
        self.__applyStyleSheet()
        self.__uiHintSourceColumns = []
        self.__buildWidgets()

        # getting configuration directory from the args
        if len(argv) > 1:
            self.__configurationDirectory = argv[1]

        # otherwise from the environment
        elif 'CENTIPEDEAPP_CONFIG_DIR' in os.environ:
            self.__configurationDirectory = os.environ['CENTIPEDEAPP_CONFIG_DIR']

        if self.updateConfiguration():
            self.__main.setWindowTitle('Centipede ({0})'.format(self.__configurationDirectory))

            # getting source files directory from the args
            if len(argv) > 2:
                self.__sourcePath.setText(':'.join(argv[2:]))

    def updateConfiguration(self):
        """
        Update the configuration used by centipede.
        """
        taskHolders = []
        currentVisibleCrawlers = self.__visibleCrawlers()

        def __camelCaseToSpaced(text):
            return text[0].upper() + re.sub("([a-z])([A-Z])","\g<1> \g<2>", text[1:])

        while not taskHolders:

            if self.__configurationDirectory == "":
                self.__configurationDirectory = QtWidgets.QFileDialog.getExistingDirectory(
                    self.__main,
                    "Select a directory with the configuration that should be used by centipede",
                    self.__configurationDirectory,
                    QtWidgets.QFileDialog.ShowDirsOnly
                )

                # cancelled
                if self.__configurationDirectory == "":
                    self.__main.deleteLater()
                    return False

            # collecting task holders from the directory
            taskHolderLoader = centipede.TaskHolderLoader.JsonLoader()
            try:
                taskHolderLoader.addFromJsonDirectory(self.__configurationDirectory)
            except Exception as err:
                QtWidgets.QMessageBox.critical(
                   self.__main,
                   "Centipede",
                   "Failed to load the configuration ({0}):\n{1}".format(
                       self.__configurationDirectory,
                       str(err)
                   ),
                   QtWidgets.QMessageBox.Ok
                )

                raise err

            if not taskHolderLoader.taskHolders():
                result = QtWidgets.QMessageBox.warning(
                    self.__main,
                    "Centipede",
                    "Selected directory does not contain any configuration for centipede!",
                    QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok,
                )

                self.__configurationDirectory = ""

                # cancelled
                if result != QtWidgets.QMessageBox.Ok:
                    self.__main.deleteLater()
                    return False

            else:
                taskHolders = taskHolderLoader.taskHolders()
                columns = []
                for taskHolder in taskHolders:
                    if '__uiHintSourceColumns' in taskHolder.varNames():
                        for columnName in taskHolder.var('__uiHintSourceColumns'):
                            if columnName not in columns:
                                columns.append(columnName)

                if columns != self.__uiHintSourceColumns:
                    self.__uiHintSourceColumns = columns
                    header = QtWidgets.QTreeWidgetItem(
                        ["Source"] + list(map(__camelCaseToSpaced, self.__uiHintSourceColumns))
                    )

                    self.__sourceTree.setHeaderItem(
                        header
                    )

        self.__taskHolders = taskHolders
        self.__onRefreshSourceDir()

        totalRows = self.__sourceTree.model().rowCount()
        result = []

        for i in range(totalRows):
            crawler = self.__sourceViewCrawlerList[i]

            if not self.__sourceTree.isRowHidden(i, QtCore.QModelIndex()):
                visible = False
                for visibleCrawler in currentVisibleCrawlers:
                    if isinstance(visibleCrawler, list):
                        useVisibleCrawler = visibleCrawler[0]
                    else:
                        useVisibleCrawler = visibleCrawler

                    if isinstance(crawler, list):
                        useCrawler = crawler[0]
                    else:
                        useCrawler = crawler

                    if useVisibleCrawler.var('filePath') == useCrawler.var('filePath'):
                        visible = True
                        break

                item = self.__sourceTree.topLevelItem(i)

                if not visible:
                    item.setCheckState(0, QtCore.Qt.Unchecked)
        return True

    def updateSource(self, path):
        """
        Update the source tree.
        """
        self.__sourceTree.clear()
        self.__sourceViewCrawlerList = []
        self.__sourceFilterMenu.clear()
        self.__sourceOverrides = self.__loadSourceOverrides()

        if not path:
            return

        # we want to list in the interface only the crawler types used by the main tasks
        filterTypes = []
        for taskHolder in self.__taskHolders:
            matchTypes = taskHolder.pathCrawlerMatcher().matchTypes()

            # if there is a task holder that does not have any type specified to it, then we display all crawlers by
            # passing an empty list to the filter
            if len(matchTypes) == 0:
                filterTypes = []
                break

            filterTypes += taskHolder.pathCrawlerMatcher().matchTypes()

        # globbing crawlers
        crawlerList = []
        for pathItem in path.split(';'):
            crawler = centipede.Crawler.Fs.FsPath.createFromPath(pathItem)
            crawlerList += crawler.glob(filterTypes)

        # in centipede interface we don't care about directory crawlers
        # TODO: we need to have a better way to get rid of directory crawlers
        crawlerList = list(filter(lambda x: not isinstance(x, centipede.Crawler.Fs.Directory), crawlerList))

        # sorting result by name
        crawlerList.sort(key=lambda x: x.var('name').lower())

        crawlerTypes = set()
        crawlerTags = {}

        # group
        if self.__checkedViewMode == "Group":
            groupedCrawlers = OrderedDict()
            groupedCrawlers[None] = []
            for crawler in crawlerList:
                if 'group' in crawler.tagNames():
                    groupName = crawler.tag('group')
                    if groupName not in groupedCrawlers:
                        groupedCrawlers[groupName] = []
                    groupedCrawlers[groupName].append(crawler)
                else:
                    groupedCrawlers[None].append(crawler)

            for groupName in groupedCrawlers.keys():
                if groupName:
                    parent = QtWidgets.QTreeWidgetItem(self.__sourceTree)

                    # visible data
                    visibleGroupName = groupName + '   '
                    if visibleGroupName.startswith(os.sep):
                        visibleGroupName = visibleGroupName[1:]

                    parent.setData(0, QtCore.Qt.EditRole, visibleGroupName)

                    # adding column information
                    self.__addSourceTreeColumnData(groupedCrawlers[groupName][0], parent)

                    parent.setFlags(parent.flags() | QtCore.Qt.ItemIsUserCheckable)
                    parent.setCheckState(0, QtCore.Qt.Checked)

                    self.__sourceViewCrawlerList.append(groupedCrawlers[groupName])
                    for crawler in groupedCrawlers[groupName]:
                        self.__createSourceTreeChildItem(
                            crawler,
                            parent,
                            crawlerTypes,
                            crawlerTags
                        )

                else:
                    for crawler in groupedCrawlers[groupName]:
                        self.__sourceViewCrawlerList.append(crawler)
                        child = self.__createSourceTreeChildItem(
                            crawler,
                            self.__sourceTree,
                            crawlerTypes,
                            crawlerTags
                        )

                        child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
                        child.setCheckState(0, QtCore.Qt.Checked)

                        self.__addSourceTreeColumnData(crawler, child)

        # flat
        else:
            for crawler in crawlerList:

                # only testing with the first crawler when grouped
                if isinstance(crawler, list):
                    crawler = crawler[0]

                self.__sourceViewCrawlerList.append(crawler)
                child = self.__createSourceTreeChildItem(crawler, self.__sourceTree, crawlerTypes, crawlerTags)
                child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
                child.setCheckState(0, QtCore.Qt.Checked)
                self.__addSourceTreeColumnData(crawler, child)

        # crawler types
        self.__crawlerTypesMenu = self.__sourceFilterMenu.addMenu('Types')

        allAction = self.__crawlerTypesMenu.addAction('ALL')
        allAction.triggered.connect(self.__onFilterSelectAll)

        noneAction = self.__crawlerTypesMenu.addAction('NONE')
        noneAction.triggered.connect(self.__onFilterSelectNone)
        self.__crawlerTypesMenu.addSeparator()

        for crawlerType in sorted(crawlerTypes):
            action = self.__crawlerTypesMenu.addAction(crawlerType)
            action.setCheckable(True)
            action.setChecked(True)
            action.changed.connect(self.__onSourceFiltersChanged)

        self.__sourceTree.resizeColumnToContents(0)

    def updateTarget(self):
        """
        Update the target tree.
        """
        self.updateConfiguration()

        visibleCrawlers = self.__visibleCrawlers()

        # applying overrides
        overrides = self.__loadSourceOverrides()
        for crawler in visibleCrawlers:
            filePath = crawler.var('filePath')
            if filePath in overrides:
                for varName, varValue in overrides[filePath].items():
                    crawler.setVar(varName, varValue)

        self.__targetAreaWidget.setVisible(True)
        self.__runOnTheFarmCheckbox.setVisible(True)
        self.__sourceAreaWidget.setVisible(False)

        self.__nextButton.setVisible(False)
        self.__backButton.setVisible(True)
        self.__runButton.setVisible(True)

        templates = []

        self.__targetTree.clear()

        for taskHolder in self.__taskHolders:

            try:
                matchedCrawlers = taskHolder.query(visibleCrawlers)
            except Exception as error:
                QtWidgets.QMessageBox.critical(
                    self.__main,
                    "Template processing error",
                    "<nobr>" + str(error).replace("\n", "<br>") + "</nobr>",
                    QtWidgets.QMessageBox.Ok,
                )
                raise error

            groupedCrawlers = OrderedDict()
            groupedCrawlers[None] = []
            for matchedCrawler in matchedCrawlers.keys():

                # group
                if self.__checkedViewMode == "Group" and 'group' in matchedCrawler.tagNames():
                    groupName = matchedCrawler.tag('group')
                    if groupName not in groupedCrawlers:
                        groupedCrawlers[groupName] = []

                    groupedCrawlers[groupName].append(matchedCrawler)

                # flat
                else:
                    groupedCrawlers[None].append(matchedCrawler)

            for groupName, crawlerList in groupedCrawlers.items():
                for crawler in crawlerList:

                    nameSuffix = ""
                    if groupName is not None:
                        nameSuffix = " (+{0} files)".format(len(crawlerList)-1)

                    matchedChild = QtWidgets.QTreeWidgetItem(self.__targetTree)
                    matchedChild.setData(0, QtCore.Qt.EditRole, matchedCrawlers[crawler] + nameSuffix)

                    mainTask = QtWidgets.QTreeWidgetItem(matchedChild)
                    mainTask.setData(0, QtCore.Qt.EditRole, "Task")

                    taskName = QtWidgets.QTreeWidgetItem(mainTask)
                    taskName.setData(0, QtCore.Qt.EditRole, "Name")

                    taskNameValue = QtWidgets.QTreeWidgetItem(taskName)
                    taskNameValue.setData(0, QtCore.Qt.EditRole, type(taskHolder.task()).__name__)

                    if 'configName' in taskHolder.varNames():
                        configName = QtWidgets.QTreeWidgetItem(mainTask)
                        configName.setData(0, QtCore.Qt.EditRole, "Config")

                        configNameValue = QtWidgets.QTreeWidgetItem(configName)
                        configNameValue.setData(
                            0,
                            QtCore.Qt.EditRole,
                            os.path.join(
                                taskHolder.var('configPath'),
                                taskHolder.var('configName')
                            )
                        )

                    templateEntry = QtWidgets.QTreeWidgetItem(mainTask)
                    templateEntry.setData(0, QtCore.Qt.EditRole, 'Template')

                    templateChild = QtWidgets.QTreeWidgetItem(templateEntry)
                    templateChild.setData(0, QtCore.Qt.EditRole, taskHolder.targetTemplate().inputString())

                    # tasks
                    self.__createSubtasks(mainTask, taskHolder)

                    if groupName is not None:
                        filesEntry = QtWidgets.QTreeWidgetItem(matchedChild)
                        filesEntry.setData(0, QtCore.Qt.EditRole, 'All Files')

                        for childCrawler in crawlerList:
                            child = QtWidgets.QTreeWidgetItem(filesEntry)
                            child.setData(0, QtCore.Qt.EditRole, matchedCrawlers[childCrawler])
                        break


        self.__targetTree.resizeColumnToContents(0)

    def __buildWidgets(self):
        """
        Create the widgets.
        """
        self.__main = QtWidgets.QMainWindow()
        self.__main.setWindowTitle('Centipede')
        self.__main.resize(1080, 720)
        self.__main.setWindowIcon(
            QtGui.QIcon(self.__uiResource("icons/centipede.png"))
        )

        centralWidget = QtWidgets.QWidget()
        self.__main.setCentralWidget(centralWidget)

        centralWidget.setLayout(QtWidgets.QVBoxLayout())
        treeArea = QtWidgets.QSplitter()

        sourceLayout = QtWidgets.QVBoxLayout()
        sourceBarLayout = QtWidgets.QHBoxLayout()

        self.__sourcePath = QtWidgets.QLineEdit()
        self.__sourcePath.setReadOnly(True)
        self.__sourceDirButton = QtWidgets.QPushButton()
        self.__sourceDirButton.setToolTip('Selects a source directory')
        self.__sourceDirButton.setIcon(
            QtGui.QIcon(self.__uiResource("icons/folder.png"))
        )

        # refresh
        self.__sourceRefreshButton = QtWidgets.QPushButton()
        self.__sourceRefreshButton.setToolTip('Refreshes the source directory')
        self.__sourceRefreshButton.setVisible(False)
        self.__sourceRefreshButton.setIcon(
            self.__sourceRefreshButton.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload)
        )

        # view mode
        self.__sourceViewModeButton = QtWidgets.QPushButton("View Mode")
        self.__sourceViewModeButton.setToolTip('Changes the view mode')
        self.__sourceViewModeButton.setIcon(
            QtGui.QIcon(self.__uiResource("icons/viewMode.png"))
        )
        self.__sourceViewModeMenu = QtWidgets.QMenu(self.__sourceViewModeButton)
        self.__sourceViewModeButton.setMenu(self.__sourceViewModeMenu)

        # filter
        self.__sourceFilterButton = QtWidgets.QPushButton("Filter View")
        self.__sourceFilterButton.setToolTip('Filters out specific crawler types')
        self.__sourceFilterButton.setIcon(
            QtGui.QIcon(self.__uiResource("icons/filterView.png"))
        )
        self.__sourceFilterMenu = QtWidgets.QMenu(self.__sourceFilterButton)
        self.__sourceFilterButton.setMenu(self.__sourceFilterMenu)

        self.__sourceDirButton.clicked.connect(self.__onSelectSourceDir)
        self.__sourceRefreshButton.clicked.connect(self.__onRefreshSourceDir)
        self.__sourcePath.textChanged.connect(self.updateSource)

        sourceBarLayout.addWidget(self.__sourceDirButton)
        sourceBarLayout.addWidget(self.__sourcePath)
        sourceBarLayout.addWidget(self.__sourceRefreshButton)
        sourceBarLayout.addWidget(self.__sourceViewModeButton)
        sourceBarLayout.addWidget(self.__sourceFilterButton)

        sourceLayout.addLayout(sourceBarLayout)

        self.__sourceAreaWidget = QtWidgets.QWidget()
        self.__sourceAreaWidget.setLayout(sourceLayout)

        targetLayout = QtWidgets.QVBoxLayout()

        self.__nextButton = QtWidgets.QPushButton("Next")
        self.__nextButton.setIcon(
            QtGui.QIcon(self.__uiResource("icons/next.png"))
        )
        self.__nextButton.clicked.connect(self.updateTarget)

        self.__backButton = QtWidgets.QPushButton("Back")
        self.__backButton.setIcon(
            QtGui.QIcon(self.__uiResource("icons/back.png"))
        )
        self.__backButton.setVisible(False)
        self.__backButton.clicked.connect(self.__onBack)

        self.__targetAreaWidget = QtWidgets.QWidget()
        self.__targetAreaWidget.setVisible(False)
        self.__targetAreaWidget.setLayout(targetLayout)
        self.__runOnTheFarmCheckbox = QtWidgets.QCheckBox("Run on the farm")
        if self.__runOnTheFarm and self.__runOnTheFarm.lower() in ["true", "1"]:
            self.__runOnTheFarmCheckbox.setChecked(True)
        self.__runOnTheFarmCheckbox.setVisible(False)

        targetBarLayout = QtWidgets.QHBoxLayout()
        targetLayout.addLayout(targetBarLayout)

        treeArea.addWidget(self.__sourceAreaWidget)
        treeArea.addWidget(self.__targetAreaWidget)

        self.__sourceTree = self.__treeWidget(["Source"])
        self.__sourceTree.itemChanged.connect(self.__onSourceTreeItemCheckedChanged)
        self.__sourceTree.customContextMenuRequested.connect(self.__onSourceTreeContextMenu)

        self.__targetTree = self.__treeWidget(["Target"])
        self.__targetTree.customContextMenuRequested.connect(self.__onTargetTreeContextMenu)

        sourceLayout.addWidget(self.__sourceTree)
        targetLayout.addWidget(self.__targetTree)

        # header
        headerLayout = QtWidgets.QHBoxLayout()
        centralWidget.layout().addLayout(headerLayout)

        logo = QtWidgets.QLabel()

        logo.setPixmap(QtGui.QPixmap(self.__uiResource("icons/header.png")).scaledToHeight(64, QtCore.Qt.SmoothTransformation))
        logo.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        headerLayout.addWidget(
            logo
        )

        headerLayout.addStretch()

        centralWidget.layout().addWidget(treeArea)
        buttonLayout = QtWidgets.QHBoxLayout()
        centralWidget.layout().addLayout(buttonLayout)

        self.__runButton = QtWidgets.QPushButton('Run')
        self.__runButton.setVisible(False)
        self.__runButton.setToolTip('Performs the tasks')
        self.__runButton.setIcon(
            QtGui.QIcon(self.__uiResource("icons/run.png"))
        )
        self.__runButton.clicked.connect(self.__onPerformTasks)

        buttonLayout.addWidget(self.__runOnTheFarmCheckbox)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.__backButton)
        buttonLayout.addWidget(self.__nextButton)
        buttonLayout.addWidget(self.__runButton)

        self.__main.show()

        # updating view mode
        self.__viewModeActionGroup = QtWidgets.QActionGroup(self)
        self.__checkedViewMode = None
        for viewMode in self.__viewModes:
            viewAction = self.__sourceViewModeMenu.addAction(viewMode.capitalize())
            viewAction.setActionGroup(self.__viewModeActionGroup)
            viewAction.setCheckable(True)
            viewAction.changed.connect(self.__onChangeView)

            if (viewMode == self.__viewModes[0]):
                viewAction.setChecked(True)

    def __launchDefaultApp(self, filePath):
        """
        Open the input file path in the default app.
        """
        subprocess.Popen(
            ['xdg-open', filePath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def __treeWidget(self, columns=[]):
        """
        Return a tree widget used by source and target.
        """
        sourceTree = QtWidgets.QTreeWidget()

        sourceTree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        sourceTree.setSelectionBehavior(QtWidgets.QTreeWidget.SelectItems)
        sourceTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        header = QtWidgets.QTreeWidgetItem(columns)
        sourceTree.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        sourceTree.setHeaderItem(header)

        return sourceTree

    def __visibleCrawlers(self):
        """
        Return a list of visible crawlers in the source tree.
        """
        totalRows = self.__sourceTree.model().rowCount()
        result = []
        for i in range(totalRows):
            self.__sourceTree.model().index(i, 0)
            if not self.__sourceTree.isRowHidden(i, QtCore.QModelIndex()):
                item = self.__sourceTree.topLevelItem(i)
                if item.checkState(0):

                    crawler = self.__sourceViewCrawlerList[i]
                    if isinstance(crawler, list):
                        result += crawler
                    else:
                        result.append(crawler)

        return list(map(lambda x: x.clone(), result))

    def __createSubtasks(self, parentEntry, taskHolder):
        """
        Create the sub tasks widget information.
        """
        if taskHolder.subTaskHolders():
            subTaskChild = QtWidgets.QTreeWidgetItem(parentEntry)
            subTaskChild.setData(0, QtCore.Qt.EditRole, 'Sub tasks')

            for childTaskHolder in taskHolder.subTaskHolders():
                taskName = type(childTaskHolder.task()).__name__

                taskChild = QtWidgets.QTreeWidgetItem(subTaskChild)
                taskChild.setData(0, QtCore.Qt.EditRole, taskName)

                templateEntry = QtWidgets.QTreeWidgetItem(taskChild)
                templateEntry.setData(0, QtCore.Qt.EditRole, 'Template')

                templateChild = QtWidgets.QTreeWidgetItem(templateEntry)
                templateChild.setData(0, QtCore.Qt.EditRole, childTaskHolder.targetTemplate().inputString())

                self.__createSubtasks(taskChild, childTaskHolder)

    def __sourceOverridesConfig(self):
        """
        Return the full path about the location for the override files.
        """
        return os.path.join(self.__configurationDirectory, "overrides", "source.json")

    def __loadSourceOverrides(self):
        """
        Load crawler overrides in the source tree.
        """
        result = {}

        if os.path.exists(self.__sourceOverridesConfig()):
            with open(self.__sourceOverridesConfig()) as sourceFile:
                result = json.load(sourceFile)

        return result

    def __addSourceTreeColumnData(self, crawler, treeItem):
        """
        Add crawler information to a column in the source tree.
        """
        # adding column information
        for index, column in enumerate(self.__uiHintSourceColumns):

            hasOverride = False
            value = ''
            if crawler.var('filePath') in self.__sourceOverrides and column in self.__sourceOverrides[crawler.var('filePath')]:
                value = self.__sourceOverrides[crawler.var('filePath')][column]
                hasOverride = True

            if column in crawler.varNames():
                if not hasOverride:
                    value = crawler.var(column)

            treeItem.setData(
                index + 1,
                QtCore.Qt.EditRole,
                str(value) +  '   '
            )

            if hasOverride:
                font = QtGui.QFont()
                font.setItalic(True)
                treeItem.setFont(
                    index + 1,
                    font
                )

                treeItem.setForeground(
                    index + 1,
                    QtGui.QBrush(QtGui.QColor(255, 152, 28))
                )

    def __createSourceTreeChildItem(self, crawler, parent, crawlerTypes, crawlerTags):
        """
        Create a new child item in the source tree.
        """
        child = QtWidgets.QTreeWidgetItem(parent)

        # visible data
        child.setData(0, QtCore.Qt.EditRole, crawler.var('baseName') + '   ')
        self.__addSourceTreeColumnData(crawler, child)

        crawlerTypes.add(crawler.var('type'))

        # adding tags
        for tagName in crawler.tagNames():
            if tagName not in crawlerTags:
                crawlerTags[tagName] = set()
            crawlerTags[tagName].add(crawler.tag(tagName))

        variables = QtWidgets.QTreeWidgetItem(child)
        variables.setData(
            0,
            QtCore.Qt.EditRole,
            'vars'
        )
        for varName in sorted(crawler.varNames()):

            if varName in ['path']:
                continue

            variablesChild = QtWidgets.QTreeWidgetItem(variables)
            variablesChild.setData(
                0,
                QtCore.Qt.EditRole,
                '{0}={1}'.format(varName, crawler.var(varName))
            )

        tags = QtWidgets.QTreeWidgetItem(child)
        tags.setData(
            0,
            QtCore.Qt.EditRole,
            'tags'
        )

        for tagName in sorted(crawler.tagNames()):
            tagChild = QtWidgets.QTreeWidgetItem(tags)
            tagChild.setData(
                0,
                QtCore.Qt.EditRole,
                '{0}={1}'.format(tagName, crawler.tag(tagName))
            )

        return child

    def __onBack(self):
        """
        Callback called when back button is triggered.
        """
        self.__runOnTheFarmCheckbox.setVisible(False)
        self.__backButton.setVisible(False)
        self.__nextButton.setVisible(True)
        self.__runButton.setVisible(False)
        self.__sourceAreaWidget.setVisible(True)
        self.__targetAreaWidget.setVisible(False)

    def __onChangeView(self):
        """
        Callback called when change view mode is triggered.
        """
        checkedAction = self.__viewModeActionGroup.checkedAction()
        if checkedAction and checkedAction.text() != self.__checkedViewMode:
            self.__checkedViewMode = self.__viewModeActionGroup.checkedAction().text()
            self.__onRefreshSourceDir()

    def __onPerformTasks(self, showConfirmation=True):
        """
        Callback called when run button is triggered.
        """
        if not self.__targetTree.model().rowCount():
            QtWidgets.QMessageBox.information(
                self.__main,
                "Centipede",
                "No targets available (refresh the targets)!",
                QtWidgets.QMessageBox.Ok
            )
            return

        visibleCrawlers = self.__visibleCrawlers()

        # applying overrides
        overrides = self.__loadSourceOverrides()
        if overrides:
            for crawler in visibleCrawlers:
                filePath = crawler.var('filePath')
                if filePath in overrides:
                    for varName, varValue in overrides[filePath].items():
                        crawler.setVar(varName, varValue)

        try:
            for crawlersGroup in Crawler.group(visibleCrawlers):
                for taskHolder in self.__taskHolders:

                    # run on the farm
                    if self.__runOnTheFarmCheckbox.checkState() == QtCore.Qt.Checked:
                        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        renderFarmDispatcher = Dispatcher.create('renderFarm')
                        label = os.path.basename(taskHolder.var('configPath'))
                        label += "/"
                        label += os.path.splitext(taskHolder.var('configName'))[0]
                        label += date
                        label += ": "
                        label += crawlersGroup[0].tag('group') if 'group' in crawlersGroup[0].tagNames() else crawlersGroup[0].var('baseName')
                        renderFarmDispatcher.setOption('label', label)
                        renderFarmDispatcher.dispatch(taskHolder, crawlersGroup)

                    # run locally
                    else:
                        localDispatcher = Dispatcher.create('local')
                        localDispatcher.dispatch(taskHolder, crawlersGroup)

        except Exception as err:
            QtWidgets.QMessageBox.critical(
               self.__main,
               "Centipede",
               "Failed during execution:\n{0}".format(
                    str(err)
               ),
               QtWidgets.QMessageBox.Ok
            )

            raise err

        else:
            if showConfirmation:
                message = "Execution completed successfully!"
                if self.__runOnTheFarmCheckbox.checkState() == QtCore.Qt.Checked:
                    message = "Execution submitted to the farm!"

                QtWidgets.QMessageBox.information(
                    self.__main,
                    "Centipede",
                    message,
                    QtWidgets.QMessageBox.Ok
                )

    def __onSourceTreeContextMenu(self, point):
        """
        Callback called when context menu from source tree is triggered.
        """
        self.__sourceTree.resizeColumnToContents(0)

        selectedIndexes = self.__sourceTree.selectionModel().selectedIndexes()

        if selectedIndexes:
            selectedColumn = selectedIndexes[0].column()
            menu = QtWidgets.QMenu(self.__main)
            if selectedColumn == 0:
                action = menu.addAction('Show Folder')
                action.triggered.connect(self.__onShowFolder)

                action = menu.addAction('Play in RV')
                action.triggered.connect(self.__onPlaySelectedInRv)
            else:
                action = menu.addAction('Override Value')
                action.triggered.connect(self.__onChangeCrawlerValue)

                action = menu.addAction('Reset Value')
                action.triggered.connect(self.__onResetCrawlerValue)

            menu.exec_(self.__sourceTree.mapToGlobal(point))

    def __onChangeCrawlerValue(self):
        """
        Callback triggered when an override in the source tree is triggered.
        """
        value = None
        overrides = dict(self.__sourceOverrides)
        for selectedIndex in self.__sourceTree.selectionModel().selectedIndexes():
            selectedColumn = selectedIndex.column()

            if selectedIndex.parent().row() != -1:
                continue

            columnName = self.__uiHintSourceColumns[selectedColumn - 1]

            crawler = self.__sourceViewCrawlerList[selectedIndex.row()]
            if not isinstance(crawler, list):
                crawler = [crawler]

            hintValue = ""
            if columnName in crawler[0].varNames():
                hintValue = crawler[0].var(columnName)

            if value is None:
                value = QtWidgets.QInputDialog.getText(
                    self.__main,
                    "Override Value",
                    "New Value",
                    QtWidgets.QLineEdit.Normal,
                    str(hintValue)
                )

                # cancelled
                if not value[1]:
                    return

                value = type(hintValue)(value[0])

            for crawlerItem in crawler:
                if crawlerItem.var('filePath') not in overrides:
                    overrides[crawlerItem.var('filePath')] = {}

                overrides[crawlerItem.var('filePath')][columnName] = value

        if not os.path.exists(os.path.dirname(self.__sourceOverridesConfig())):
            os.mkdir(os.path.dirname(self.__sourceOverridesConfig()))

        with open(self.__sourceOverridesConfig(), 'w') as sourceFile:
            json.dump(overrides, sourceFile, indent=4)

        if value is not None:
            self.__onRefreshSourceDir()

    def __onResetCrawlerValue(self):
        """
        Callback triggered when an override in the source tree is removed.
        """
        overrides = dict(self.__sourceOverrides)
        for selectedIndex in self.__sourceTree.selectionModel().selectedIndexes():
            selectedColumn = selectedIndex.column()

            if selectedIndex.parent().row() != -1:
                continue

            columnName = self.__uiHintSourceColumns[selectedColumn - 1]

            crawler = self.__sourceViewCrawlerList[selectedIndex.row()]
            if not isinstance(crawler, list):
                crawler = [crawler]

            crawlerFilePaths = map(lambda x: x.var('filePath'), crawler)
            for filePath in crawlerFilePaths:
                if filePath in overrides:
                    if columnName in overrides[filePath]:
                        del overrides[filePath][columnName]

                    if not len(overrides[filePath]):
                        del overrides[filePath]

        if os.path.exists(os.path.dirname(self.__sourceOverridesConfig())):
            with open(self.__sourceOverridesConfig(), 'w') as sourceFile:
                json.dump(overrides, sourceFile, indent=4)

            self.__onRefreshSourceDir()

    def __onTargetTreeContextMenu(self, point):
        """
        Callback triggered when the context menu in the target tree is triggered.
        """
        selectedIndexes = self.__targetTree.selectionModel().selectedIndexes()
        if selectedIndexes:
            value = selectedIndexes[0].data(0)

            if str(value).endswith('.json'):
                menu = QtWidgets.QMenu(self.__main)
                action = menu.addAction('Show Config')
                action.triggered.connect(functools.partial(self.__launchDefaultApp, value))

                menu.exec_(self.__sourceTree.mapToGlobal(point))

    def __onShowFolder(self):
        """
        Callback called when show folder for the selected crawlers is triggered.
        """
        folderPaths = set()
        for index, crawler in enumerate(self.__sourceViewCrawlerList):

            if isinstance(crawler, list):
                crawler = crawler[0]

            item = self.__sourceTree.topLevelItem(index)
            if item.isSelected():
                folderPaths.add(os.path.dirname(crawler.var('filePath')))

        for folderPath in folderPaths:
            self.__launchDefaultApp(
                folderPath
            )

    def __onPlaySelectedInRv(self):
        """
        Callback called when play select in rv is triggered.
        """
        folderPaths = []
        for index, crawler in enumerate(self.__sourceViewCrawlerList):

            if isinstance(crawler, list):
                crawler = crawler[0]

            item = self.__sourceTree.topLevelItem(index)
            if item.isSelected():
                folderPaths.append(crawler.var('filePath'))

        subprocess.Popen(
            ['rv', ' '.join(folderPaths)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def __onSelectSourceDir(self):
        """
        Callback called when select source button is triggered.
        """
        currentDir = self.__sourcePath.text() or '/'
        selectedDirectory = QtWidgets.QFileDialog.getExistingDirectory(
            self.__main,
            "Select source directory",
            currentDir,
            QtWidgets.QFileDialog.ShowDirsOnly
        )

        if selectedDirectory not in ['', '/']:
            self.__sourcePath.setText(selectedDirectory)

    def __onRefreshSourceDir(self):
        """
        Callback called when refresh button from source tree is triggered.
        """
        self.updateSource(self.__sourcePath.text())

    def __onFilterSelectNone(self):
        """
        Callback called when select none filter is triggered.
        """
        self.__onFilterSelectAll(False)

    def __onFilterSelectAll(self, checked=True):
        """
        Callback called when select all filter is triggered.
        """
        for action in self.__crawlerTypesMenu.actions():
            action.setChecked(checked)

    def __onSourceFiltersChanged(self):
        """
        Callback triggered a filter is changed in the source tree.
        """
        visibleTypes = []
        for action in self.__crawlerTypesMenu.actions():
            if action.isChecked():
                visibleTypes.append(action.text())

        totalRows = self.__sourceTree.model().rowCount()
        for i in range(totalRows):
            crawler = self.__sourceViewCrawlerList[i]

            # only testing with the first crawler when grouped
            if isinstance(crawler, list):
                crawler = crawler[0]

            self.__sourceTree.model().index(i, 0)

            self.__sourceTree.setRowHidden(
                i,
                QtCore.QModelIndex(),
                (crawler.var('type') not in visibleTypes)
            )

    def __onSourceTreeItemCheckedChanged(self, currentItem):
        """
        Callback called when the check state of an item in the source tree is changed.
        """
        if currentItem.isSelected():
            if self.__sourceTree.selectionModel().selectedIndexes():
                for index in range(len(self.__sourceViewCrawlerList)):
                    item = self.__sourceTree.topLevelItem(index)
                    if item.isSelected():
                        item.setCheckState(0, currentItem.checkState(0))

    def __applyStyleSheet(self):
        """
        Apply the default stylesheet to the ingestor interface.
        """
        self.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
        defaultFont = QtWidgets.QApplication.font()
        defaultFont.setPointSize(defaultFont.pointSize() + 2.0)
        self.setFont(defaultFont)

        # modify palette to dark
        darkPalette = QtGui.QPalette()
        darkPalette.setColor(
            QtGui.QPalette.Window,
            QtGui.QColor(53,53,53)
        )

        darkPalette.setColor(
            QtGui.QPalette.WindowText,
            QtCore.Qt.white
        )

        darkPalette.setColor(
            QtGui.QPalette.Disabled,
            QtGui.QPalette.WindowText,
            QtGui.QColor(127,127,127)
        )

        darkPalette.setColor(
            QtGui.QPalette.Base,
            QtGui.QColor(42,42,42)
        )

        darkPalette.setColor(
            QtGui.QPalette.AlternateBase,
            QtGui.QColor(66,66,66)
        )

        darkPalette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        darkPalette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        darkPalette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        darkPalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(127,127,127))
        darkPalette.setColor(QtGui.QPalette.Dark,QtGui.QColor(35,35,35))
        darkPalette.setColor(QtGui.QPalette.Shadow,QtGui.QColor(20,20,20))
        darkPalette.setColor(QtGui.QPalette.Button,QtGui.QColor(53,53,53))
        darkPalette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        darkPalette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ButtonText,QtGui.QColor(127,127,127))
        darkPalette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        darkPalette.setColor(QtGui.QPalette.Link,QtGui.QColor(42,130,218))
        darkPalette.setColor(QtGui.QPalette.Highlight,QtGui.QColor(42,130,218))
        darkPalette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.Highlight,QtGui.QColor(80,80,80))
        darkPalette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
        darkPalette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.HighlightedText,QtGui.QColor(127,127,127))

        self.setPalette(darkPalette)

        styleSheetFile = self.__uiResource("darkstyle/darkstyle.qss")
        styleSheetContents = '\n'.join(open(styleSheetFile, "r").readlines())
        styleSheetContents = styleSheetContents.replace("darkstyle/", '{0}/'.format(os.path.dirname(styleSheetFile)))

        self.setStyleSheet(
            styleSheetContents
        )

    @staticmethod
    def __uiResource(name):
        """
        Auxiliary method used to retrieve the full path from a resource used by the ui.
        """
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            "data",
            "ui",
            name
        )

app = CentipedeApp(sys.argv)
sys.exit(app.exec_())
