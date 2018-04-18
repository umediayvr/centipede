import os
import json
import uuid
from datetime import datetime
from collections import OrderedDict
from ..Dispatcher import Dispatcher
from .RenderfarmJob import RenderfarmJob, ExpandedJob, CollapsedJob

class Renderfarm(Dispatcher):
    """
    Abstracted implementation for a renderfarm dispatcher.

    Optional options: label, jobTempDir, splitSize, priority and expandOnTheFarm
    """

    __defaultJobTempDir = os.environ.get('UMEDIA_TEMP_REMOTE_DIR', '')
    __defaultLabel = "ingestor"
    __defaultExpandOnTheFarm = False
    __defaultPriority = 50
    __defaultSplitSize = 5

    def __init__(self, *args, **kwargs):
        """
        Create a Renderfarm dispatcher object.
        """
        super(Renderfarm, self).__init__(*args, **kwargs)

        # setting default options
        self.setOption('label', self.__defaultLabel)
        self.setOption('jobTempDir', self.__defaultJobTempDir)
        self.setOption('splitSize', self.__defaultSplitSize)
        self.setOption('priority', self.__defaultPriority)
        self.setOption('expandOnTheFarm', self.__defaultExpandOnTheFarm)

    def _perform(self, taskHolder):
        """
        Execute the dispatcher.

        Return a list of job ids.
        """
        clonedTaskHolder = taskHolder.clone()
        jobDirectory = self.__createJobDirectory()
        renderfarmJobs = []

        if self.option('expandOnTheFarm'):
            collapsedJob = CollapsedJob(
                taskHolder,
                jobDirectory
            )

            jobDataFilePath = self.__generateJobData(
                collapsedJob
            )

            # sending to the farm
            return [
                self._executeOnTheFarm(
                    collapsedJob,
                    jobDataFilePath
                )
            ]

        else:
            renderfarmJobs += self.__dispatchMainTaskHolder(
                clonedTaskHolder,
                jobDirectory
            )

        renderfarmJobs += self.__dispatchSubTaskHolders(
            clonedTaskHolder.subTaskHolders(),
            jobDirectory,
            renderfarmJobs
        )

        return list(map(lambda x: x.jobId(), renderfarmJobs))

    def _executeOnTheFarm(self, renderfarmJob, jobDataFilePath):
        """
        For re-implementation: Should dispatch the job to the farm.

        Make sure the implementation returns the job id created during the dispatch.
        """
        raise NotImplementedError

    def __generateJobData(self, renderfarmJob):
        """
        Generate a file used to execute the task holder on the farm.
        """
        assert isinstance(renderfarmJob, RenderfarmJob), \
            "Invalid RenderfarmJob type!"

        # in case the option "expandOnTheFarm" is enabled we need to disable that
        # otheriwse, the job is going to keep re-spawing on the farm indefinitely.
        renderFarmDispatcher = self
        if renderFarmDispatcher.option('expandOnTheFarm'):
            renderFarmDispatcher = renderFarmDispatcher.createFromJson(
                renderFarmDispatcher.toJson()
            )

            renderFarmDispatcher.setOption(
                'expandOnTheFarm',
                False
            )

        data = {
            'dispatcher': renderFarmDispatcher.toJson(),
            'taskHolder': renderfarmJob.taskHolder().toJson()
        }

        # collapsed job
        if isinstance(renderfarmJob, CollapsedJob):
            data['jobType'] = 'collapsed'
            data['taskInputFilePaths'] = []

            # adding the result of expanded jobs. This information is going
            # to be used as input when the job gets expanded
            for expandedJob in renderfarmJob.expandedJobs():
                data['taskInputFilePaths'].append(
                    expandedJob.taskResultFilePath()
                )

        # expanded job
        else:
            data['jobType'] = 'expanded'
            data['taskResultFilePath'] = renderfarmJob.taskResultFilePath()

        jobDataFilePath = os.path.join(
            renderfarmJob.jobDirectory(),
            "jobData_{}.json".format(
                str(uuid.uuid1())
            )
        )

        # writing out the job data
        with open(jobDataFilePath, 'w') as outputFile:
            json.dump(
                data,
                outputFile,
                indent=4
            )

        return jobDataFilePath

    def __dispatchMainTaskHolder(self, taskHolder, jobDirectory):
        """
        Dispatch the main task holder as expanded jobs on the farm.

        The result is a list of expanded job instances.
        """
        clonedTaskHolder = taskHolder.clone(includeSubTaskHolders=False)
        task = clonedTaskHolder.task()
        result = []

        # figuring out how the task is going to split the crawlers in multiple
        # tasks. In case the split size is assigned to 0 means the task is not
        # going to be divided
        splitSize = 0
        if task.hasMetadata('dispatch.split') and task.metadata('dispatch.split'):
            if task.hasMetadata('dispatch.splitSize'):
                splitSize = task.metadata('dispatch.splitSize')
            else:
                splitSize = self.option('splitSize')

        # querying all crawlers from the current task so we can re-assing them
        # back to the task in chuncks (when split size is greater than 0)
        pathCrawlers = OrderedDict()
        for crawler in task.pathCrawlers():
            pathCrawlers[crawler] = task.filePath(crawler)

        crawlers = list(pathCrawlers.keys())
        chunckfiedCrawlers = self.__chunkify(crawlers, splitSize) if splitSize else [crawlers]

        # splitting in multiple tasks
        for index, chunckedCrawlers in enumerate(chunckfiedCrawlers):

            # creating a renderfarm job
            expandedJob = ExpandedJob(clonedTaskHolder, jobDirectory)

            # adding information about the chunks
            expandedJob.setChunkTotal(len(chunckfiedCrawlers))
            expandedJob.setCurrentChunk(index)
            expandedJob.setChunkSize(splitSize)

            task = clonedTaskHolder.task()

            # adding crawlers to the task (since the task holder has been cloned
            # previously it's safe for us to change it)
            task.clear()
            for chunckedCrawler in chunckedCrawlers:
                targetFilePath = pathCrawlers[chunckedCrawler]
                task.add(chunckedCrawler, targetFilePath)

            jobDataFilePath = self.__generateJobData(
                expandedJob
            )

            # sending to the farm
            jobId = self._executeOnTheFarm(
                expandedJob,
                jobDataFilePath
            )

            # setting the job id to the expanded job. This information may
            # be used by sub tasks holders.
            expandedJob.setJobId(jobId)

            result.append(
                expandedJob
            )

        return result

    def __dispatchSubTaskHolders(self, subTaskHolders, jobDirectory, renderfarmJobs):
        """
        Dispatch the sub task holders as collapsed jobs on the farm.

        The result is a list of collapsed job instances.
        """
        result = []
        awaitSubtaskHolders = []

        # processing first all sub task holders that can be executed in parallel
        for subTaskHolder in subTaskHolders:
            if subTaskHolder.task().hasMetadata('dispatch.await') and subTaskHolder.task().metadata('dispatch.await'):
                awaitSubtaskHolders.append(subTaskHolder)
                continue

            collapsedJob = CollapsedJob(
                subTaskHolder,
                jobDirectory
            )

            # adding the input renderfarm jobs as dependency
            for renderfarmJob in renderfarmJobs:
                collapsedJob.addExpandedJob(renderfarmJob)
                collapsedJob.addDependencyId(renderfarmJob.jobId())

            jobDataFilePath = self.__generateJobData(
                collapsedJob
            )

            # sending to the farm
            jobId = self._executeOnTheFarm(
                collapsedJob,
                jobDataFilePath
            )

            # setting the job id to the collapsed job
            collapsedJob.setJobId(jobId)

            result.append(collapsedJob)

        # processing the awaiting sub-tasks holders. When a sub task holder is marked with
        # "await" means it is only going to be started after all the sub task holders are done,
        # making the sub task holder to be executed in a stack model rather than
        # in a parallel model.
        parentRenderfarmJobs = result
        for awaitSubtaskHolder in awaitSubtaskHolders:

            collapsedJob = CollapsedJob(
                awaitSubtaskHolder,
                jobDirectory
            )

            # adding all the expanded jobs passed as argument to this
            # method to the collapsed jobs
            for renderfarmJob in renderfarmJobs:
                collapsedJob.addExpandedJob(renderfarmJob)

            # the dependency ids are about the sub tasks holders
            # processed previously. In case there is more than
            # one await sub task holder then the dependency id
            # is going to be driven by the previous await task holder.
            for parentRenderfarmJob in parentRenderfarmJobs:
                collapsedJob.addDependencyId(parentRenderfarmJob.jobId())

            jobDataFilePath = self.__generateJobData(
                collapsedJob
            )

            # sending to the farm
            jobId = self._executeOnTheFarm(
                collapsedJob,
                jobDataFilePath
            )

            collapsedJob.setJobId(jobId)
            result.append(collapsedJob)

            # making sure the next following await task holder is going
            # to await for the current await task holder to be done
            parentRenderfarmJobs = [
                collapsedJob
            ]

        return result

    def __createJobDirectory(self):
        """
        Create a temporary job directory used to store the job configuration.
        """
        currentDate = datetime.now()
        baseRemoteTemporaryPath = os.path.join(
            self.__defaultJobTempDir,
            currentDate.strftime("%Y%m%d"),
            currentDate.strftime("%H"),
            os.environ['USERNAME'],
            str(uuid.uuid1())
        )
        os.makedirs(baseRemoteTemporaryPath)

        return baseRemoteTemporaryPath

    @classmethod
    def __chunkify(cls, inputList, chunckSize):
        """
        Return an 2D array containing the input list divided by chunks.
        """
        result = []
        if len(inputList) <= chunckSize:
            result.append(inputList)
            return result

        for chunk in range(int(len(inputList) / chunckSize)):
            currentIndex = chunk * chunckSize
            result.append(
                inputList[currentIndex:currentIndex + chunckSize]
            )

        return result
