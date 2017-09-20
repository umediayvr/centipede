import sys
import os
import re
import ingestor
import subprocess
from PySide2 import QtCore, QtGui, QtWidgets


class Application(QtWidgets.QApplication):

    def __init__(self, argv, **kwargs):
        super(Application, self).__init__(argv, **kwargs)

        self.__buildWidgets()

        # showing a dialog to pick where the task holder
        # configuration is localized
        configurationDirectory = ""

        # getting configuration directory from the args
        if len(argv) > 1:
            configurationDirectory = argv[1]

        taskHolders = []
        while not taskHolders:

            if configurationDirectory == "":
                configurationDirectory = QtWidgets.QFileDialog.getExistingDirectory(
                    self.__main,
                    "Select a directory with the configuration that should be used by the ingestor",
                    configurationDirectory,
                    QtWidgets.QFileDialog.ShowDirsOnly
                )

                # cancelled
                if configurationDirectory == "":
                    raise Exception("Ingestor Cancelled")
                    break

            # collecting path holders from the directory
            taskHolderLoader = ingestor.TaskHolderLoader.JsonLoader()
            taskHolderLoader.addFromJsonDirectory(configurationDirectory)

            if not taskHolderLoader.taskHolders():

                result = QtWidgets.QMessageBox.warning(
                    self.__main,
                    "Ingestor",
                    "Selected directory does not contain any configuration for the ingestor!",
                    QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok,
                )

                # cancelled
                if result != QtWidgets.QMessageBox.Ok:
                    raise Exception("Ingestor Cancelled")
                    break
                else:
                    configurationDirectory = ""

            else:
                taskHolders = taskHolderLoader.taskHolders()

        self.__main.setWindowTitle('Ingestor ({0})'.format(configurationDirectory))
        self.__taskHolders = taskHolders

        # getting source files directory from the args
        if len(argv) > 2:
            self.__sourcePath.setText(argv[2])

    def __buildWidgets(self):
        self.__main = QtWidgets.QMainWindow()
        self.__main.setWindowTitle('Ingestor')
        self.__main.resize(1920, 1080)

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
            self.__sourceDirButton.style().standardIcon(QtWidgets.QStyle.SP_DirIcon)
        )

        # refresh
        self.__sourceRefreshButton = QtWidgets.QPushButton()
        self.__sourceRefreshButton.setToolTip('Refreshes the source directory')
        self.__sourceRefreshButton.setVisible(False)
        self.__sourceRefreshButton.setIcon(
            self.__sourceRefreshButton.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload)
        )

        # filter
        self.__sourceFilterButton = QtWidgets.QPushButton()
        self.__sourceFilterButton.setToolTip('Filters out specific crawler types')
        self.__sourceFilterButton.setIcon(
            self.__sourceFilterButton.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView)
        )

        self.__sourceDirButton.clicked.connect(self.__onSelectSourceDir)
        self.__sourceRefreshButton.clicked.connect(self.__onRefreshSourceDir)
        self.__sourcePath.textChanged.connect(self.updateSource)

        sourceBarLayout.addWidget(self.__sourceDirButton)
        sourceBarLayout.addWidget(self.__sourcePath)
        sourceBarLayout.addWidget(self.__sourceRefreshButton)
        sourceBarLayout.addWidget(self.__sourceFilterButton)

        self.__sourceFilterMenu = QtWidgets.QMenu(self.__sourceFilterButton)
        self.__sourceFilterButton.setMenu(self.__sourceFilterMenu)

        sourceLayout.addLayout(sourceBarLayout)

        sourceAreaWidget = QtWidgets.QWidget()
        sourceAreaWidget.setLayout(sourceLayout)

        targetLayout = QtWidgets.QVBoxLayout()

        self.__refreshTarget = QtWidgets.QPushButton()
        self.__refreshTarget.setToolTip('Refreshes the target')
        self.__refreshTarget.setIcon(
            self.__refreshTarget.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload)
        )
        self.__refreshTarget.clicked.connect(self.updateTarget)

        targetAreaWidget = QtWidgets.QWidget()
        targetAreaWidget.setLayout(targetLayout)

        targetBarLayout = QtWidgets.QHBoxLayout()
        targetBarLayout.addWidget(self.__refreshTarget)

        targetLayout.addLayout(targetBarLayout)

        treeArea.addWidget(sourceAreaWidget)
        treeArea.addWidget(targetAreaWidget)

        self.__sourceTree = self.__createTreeWidget(["Source"])
        self.__sourceTree.itemChanged.connect(self.__sourceCheckChanged)
        self.__sourceTree.customContextMenuRequested.connect(self.__onSourceTreeContextMenu)

        self.__targetTree = self.__createTreeWidget(["Target"])
        self.__targetTree.itemSelectionChanged.connect(self.__onTargetSelectionChanged)

        sourceLayout.addWidget(self.__sourceTree)
        targetLayout.addWidget(self.__targetTree)

        centralWidget.layout().addWidget(treeArea)
        buttonLayout = QtWidgets.QHBoxLayout()
        centralWidget.layout().addLayout(buttonLayout)

        self.__runButton = QtWidgets.QPushButton('Run')
        self.__runButton.setToolTip('Performs the tasks')
        self.__runButton.setIcon(
            self.__runButton.style().standardIcon(QtWidgets.QStyle.SP_ArrowForward)
        )
        self.__runButton.clicked.connect(self.__onPerformTasks)

        buttonLayout.addStretch()
        buttonLayout.addWidget(self.__runButton)

        self.__main.show()

    def __onPerformTasks(self):
        """
        Execute the tasks.
        """
        if not self.__targetTree.model().rowCount():
            QtWidgets.QMessageBox.information(
                self.__main,
                "Ingestor",
                "No targets available (refresh the targets)!",
                QtWidgets.QMessageBox.Ok
            )
            return

        visibleCrawlers = self.__visibleCrawlers()
        try:
            for taskHolder in self.__taskHolders:
                self.__recursiveTaskRunner(visibleCrawlers, taskHolder)
        except Exception as err:
            QtWidgets.QMessageBox.critical(
               self.__main,
               "Ingestor",
               "Failed during the ingestion:\n{0}".format(
                    str(err)
               ),
               QtWidgets.QMessageBox.Ok
            )

            raise err

        else:
             QtWidgets.QMessageBox.information(
                self.__main,
                "Ingestor",
                "Ingestion completed successfully!",
                QtWidgets.QMessageBox.Ok
            )

    def __recursiveTaskRunner(self, crawlers, taskHolder):
        matchedCrawlers = taskHolder.query(crawlers)
        if matchedCrawlers:

            # cloning task so we can modify it
            clonedTask = taskHolder.task().clone()

            for matchedCrawler, targetFilePath in matchedCrawlers.items():

                # todo:
                # need to have a way to clone a crawler, so we can
                # modify it safely
                for customVarName in taskHolder.customVarNames():
                    matchedCrawler.setVar(
                        customVarName,
                        taskHolder.customVar(customVarName)
                    )

                clonedTask.add(matchedCrawler, targetFilePath)

            # performing task
            currentTaskName = type(clonedTask).__name__
            sys.stdout.write('Running task: {0}\n'.format(currentTaskName))
            for pathCrawler in clonedTask.run():
                sys.stdout.write('  - {0}: {1}\n'.format(
                        currentTaskName,
                        matchedCrawlers[pathCrawler]
                    )
                )
                sys.stdout.flush()

            if taskHolder.subTaskHolders():
                newCrawlers = []
                for templateGeneratedFile in set(matchedCrawlers.values()):
                    childCrawler = ingestor.Crawler.Fs.Path.create(
                        ingestor.PathHolder(templateGeneratedFile)
                    )

                    # setting the task holder custom variables to this crawler.
                    # This basically transfer the global variables declared in
                    # the json configuration to the crawler, so subtasks can use
                    # them to resolve templates (when necessary).
                    for customVarName in taskHolder.customVarNames():
                        childCrawler.setVar(
                            customVarName,
                            taskHolder.customVar(customVarName)
                        )

                    # appending the new crawler
                    newCrawlers.append(
                        childCrawler
                    )

                for subTaskHolder in taskHolder.subTaskHolders():
                    self.__recursiveTaskRunner(newCrawlers, subTaskHolder)

    def __onSourceTreeContextMenu(self, point):

        if self.__sourceTree.selectionModel().selectedIndexes():
            menu = QtWidgets.QMenu(self.__main)
            action = menu.addAction('Show Folder')
            action.triggered.connect(self.__openSelected)

            menu.exec_(self.__sourceTree.mapToGlobal(point))

    def __openSelected(self):

        folderPaths = set()
        for index, crawler in enumerate(self.__crawlerList):
            item = self.__sourceTree.topLevelItem(index)
            if item.isSelected():
                folderPaths.add(os.path.dirname(crawler.var('filePath')))


        for folderPath in folderPaths:
            subprocess.Popen(
                ['xdg-open', folderPath],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

    def __onSelectSourceDir(self):
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
        self.updateSource(self.__sourcePath.text())

    def __createTreeWidget(self, columns=[]):
        sourceTree = QtWidgets.QTreeWidget()
        sourceTree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        sourceTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        header = QtWidgets.QTreeWidgetItem(columns)
        sourceTree.header().setStretchLastSection(True)
        sourceTree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        sourceTree.setHeaderItem(header)

        return sourceTree

    def __onTargetSelectionChanged(self):
        pass

    def __visibleCrawlers(self):
        totalRows = self.__sourceTree.model().rowCount()
        result = []
        for i in range(totalRows):
            self.__sourceTree.model().index(i, 0)
            if not self.__sourceTree.isRowHidden(i, QtCore.QModelIndex()):
                item = self.__sourceTree.topLevelItem(i)
                if item.checkState(0):
                    result.append(self.__crawlerList[i])

        return result

    def updateTarget(self):
        visibleCrawlers = self.__visibleCrawlers()

        templates = []

        self.__targetTree.clear()

        for taskHolder in self.__taskHolders:
            matchedCrawlers = taskHolder.query(visibleCrawlers)

            child = QtWidgets.QTreeWidgetItem(self.__targetTree)
            child.setData(0, QtCore.Qt.EditRole, type(taskHolder.task()).__name__)
            #child.setExpanded(True)

            templateEntry = QtWidgets.QTreeWidgetItem(child)
            templateEntry.setData(0, QtCore.Qt.EditRole, 'template')

            templateChild = QtWidgets.QTreeWidgetItem(templateEntry)
            templateChild.setData(0, QtCore.Qt.EditRole, taskHolder.targetTemplate().inputString())

            # missing selection sync with the source side
            fileEntry = QtWidgets.QTreeWidgetItem(child)
            fileEntry.setData(0, QtCore.Qt.EditRole, 'files')
            fileEntry.setExpanded(True)

            for matchedCrawler, targetFilePath in matchedCrawlers.items():
                matchedChild = QtWidgets.QTreeWidgetItem(fileEntry)
                matchedChild.setData(0, QtCore.Qt.EditRole, targetFilePath)

            # tasks (missing checkbox to enable the task?)
            self.__createSubtasks(child, taskHolder)

        self.__targetTree.resizeColumnToContents(0)

    def __createSubtasks(self, parentEntry, taskHolder):
        if taskHolder.subTaskHolders():
            subTaskChild = QtWidgets.QTreeWidgetItem(parentEntry)
            subTaskChild.setData(0, QtCore.Qt.EditRole, 'sub tasks')

            for childTaskHolder in taskHolder.subTaskHolders():
                taskName = type(childTaskHolder.task()).__name__

                taskChild = QtWidgets.QTreeWidgetItem(subTaskChild)
                taskChild.setData(0, QtCore.Qt.EditRole, taskName)

                templateEntry = QtWidgets.QTreeWidgetItem(taskChild)
                templateEntry.setData(0, QtCore.Qt.EditRole, 'template')

                templateChild = QtWidgets.QTreeWidgetItem(templateEntry)
                templateChild.setData(0, QtCore.Qt.EditRole, childTaskHolder.targetTemplate().inputString())

                self.__createSubtasks(subTaskChild, childTaskHolder)

    def __collectCrawlers(self, crawler):
        result = []
        result.append(crawler)

        if not crawler.isLeaf():
            for childCrawler in crawler.children():
                result += self.__collectCrawlers(childCrawler)

        return result

    def updateSource(self, path):

        ph = ingestor.PathHolder(path)
        crawler = ingestor.Crawler.Fs.Path.create(ph)
        self.__crawlerList = self.__collectCrawlers(crawler)
        self.__sourceFilterMenu.clear()

        self.__crawlerList = list(filter(lambda x: not isinstance(x, ingestor.Crawler.Fs.Directory), self.__crawlerList))
        self.__crawlerList.sort(key=lambda x: x.var('path').lower())
        crawlerTypes = set()
        crawlerTags = {}

        self.__sourceTree.clear()
        for crawler in self.__crawlerList:
            child = QtWidgets.QTreeWidgetItem(self.__sourceTree)

            # visible data
            child.setData(0, QtCore.Qt.EditRole, crawler.var('path')[1:])
            child.setData(1, QtCore.Qt.EditRole, crawler.var('type'))

            # hidden data
#            child.setData(100, QtCore.Qt.EditRole, crawler.var('path'))
            #child.setData(101, QtCore.Qt.EditRole, crawler.var('type'))
            crawlerTypes.add(crawler.var('type'))

            # adding tags
            for tagName in crawler.tagNames():
                if tagName not in crawlerTags:
                    crawlerTags[tagName] = set()
                crawlerTags[tagName].add(crawler.tag(tagName))

            child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
            child.setCheckState(0, QtCore.Qt.Checked)

            variables = QtWidgets.QTreeWidgetItem(child)
            variables.setData(
                0,
                QtCore.Qt.EditRole,
                'vars'
            )
            for varName in sorted(crawler.varNames()):

                if varName in ['filePath', 'path']:
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

    def __onFilterSelectNone(self):
        self.__onFilterSelectAll(False)

    def __onFilterSelectAll(self, checked=True):
        for action in self.__crawlerTypesMenu.actions():
            action.setChecked(checked)

    def __onSourceFiltersChanged(self):
        visibleTypes = []
        for action in self.__crawlerTypesMenu.actions():
            if action.isChecked():
                visibleTypes.append(action.text())

        totalRows = self.__sourceTree.model().rowCount()
        for i in range(totalRows):
            crawler = self.__crawlerList[i]
            self.__sourceTree.model().index(i, 0)

            self.__sourceTree.setRowHidden(
                i,
                QtCore.QModelIndex(),
                (crawler.var('type') not in visibleTypes)
            )

    def __sourceCheckChanged(self, currentItem):

        if currentItem.isSelected():
            if self.__sourceTree.selectionModel().selectedIndexes():
                for index, crawler in enumerate(self.__crawlerList):
                    item = self.__sourceTree.topLevelItem(index)
                    if item.isSelected():
                        item.setCheckState(0, currentItem.checkState(0))


app = Application(sys.argv)
#app.updateSource("/home/paulon/dev/umedia/ingestor/data")
sys.exit(app.exec_())
