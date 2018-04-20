import os
import subprocess
import tempfile
from .Renderfarm import Renderfarm
from .RenderfarmJob import RenderfarmJob, CollapsedJob, ExpandedJob

class DeadlineCommandError(Exception):
    """
    Deadline command error.
    """

class Deadline(Renderfarm):
    """
    Deadline dispatcher implementation.

    Optional options: pool, secondaryPool, group and jobFailRetryAttempts
    """

    __defaultGroup = ''
    __defaultPool = ''
    __defaultSecondaryPool = ''
    __defaultJobFailRetryAttempts = 1

    def __init__(self, *args, **kwargs):
        """
        Create a Renderfarm dispatcher object.
        """
        super(Deadline, self).__init__(*args, **kwargs)

        self.__lazyOptions = {}

        # setting default options
        self.setOption('group', self.__defaultGroup)
        self.setOption('pool', self.__defaultPool)
        self.setOption('secondaryPool', self.__defaultSecondaryPool)
        self.setOption('jobFailRetryAttempts', self.__defaultJobFailRetryAttempts)

        # deadline is extremely slow to submit jobs to the farm. Therefore,
        # we need to expand them inside of the farm rather than awaiting
        # locally for the submission of all the jobs.
        self.setOption('expandOnTheFarm', True)

        # for the same performance reason above we want to let deadline to chunkify
        # the job on the farm by default
        self.setOption('chunkifyOnTheFarm', True)

    def option(self, name, *args, **kwargs):
        """
        Return a value from an option.

        Due several performance penality caused by querying deadline command
        we need to compute 'groupNames' and 'poolNames' only when they are queried.
        """
        # computing dynamic option
        if name not in self.optionNames() and name in ['groupNames', 'poolNames']:
            if name == 'groupNames':
                command = 'deadlinecommand GetGroupNames'
            else:
                command = 'deadlinecommand GetPoolNames'

            self.setOption(
                name,
                self.__executeDeadlineCommand(
                    command
                ).split('\n')
            )

        # returning the value for an option
        return super(Deadline, self).option(name, *args, **kwargs)

    def _executeOnTheFarm(self, renderfarmJob, jobDataFilePath):
        """
        For re-implementation: Should call the subprocess that dispatches the job to the farm.

        Should return the job id created during the dispaching.
        """
        assert isinstance(renderfarmJob, RenderfarmJob), \
            "Invalid RenderFarmJob type!"

        task = renderfarmJob.taskHolder().task()
        dependencyIds = renderfarmJob.dependencyIds()
        outputDirectories = []

        # computing the command that deadline is going to trigger on the farm
        command = '{0} {1}'.format(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "aux", "execute-renderfarm.py"),
            jobDataFilePath
        )

        # in case "chunkifyOnTheFarm" is enabled we need to add the parameters about
        # the start frame and end frame. Deadline is going to provide the value
        # for them when computing the chunks on the farm
        if self.option('chunkifyOnTheFarm') and isinstance(renderfarmJob, ExpandedJob) and renderfarmJob.chunkSize():
            command += " --range-start <STARTFRAME> --range-end <ENDFRAME>"

        args = self.__defaultJobArgs(command, jobDataFilePath)

        # collapsed job
        if isinstance(renderfarmJob, CollapsedJob):
            # adding the job name
            args += [
                "-name",
                "Pending {}".format(task.type())
            ]

            # since pending jobs are intermediated jobs, we mark them to be deleted asap
            # they are completed
            args += [
                "-prop",
                "OnJobComplete=Delete"
            ]

        # expanded job type
        else:
            totalChunks = renderfarmJob.chunkTotal()
            currentChunk = renderfarmJob.currentChunk()

            # label displayed in deadline
            taskLabel = task.type()

            if self.option('chunkifyOnTheFarm') and renderfarmJob.chunkSize():
                args += [
                    "-prop",
                    "Frames=0-{}".format(renderfarmJob.totalInChunk() - 1),
                    "-prop",
                    "ChunkSize={}".format(renderfarmJob.chunkSize())
                ]
            else:
                taskLabel += ' ({}/{}): '.format(
                    str(currentChunk + 1).zfill(3),
                    str(totalChunks).zfill(3)
                )

            taskLabel += task.pathCrawlers()[0].var('name')

            args += [
                "-name",
                taskLabel
            ]

            outputDirectories = list(set(map(lambda x: os.path.dirname(task.filePath(x)), task.pathCrawlers())))
            for index, outputDirectory in enumerate(outputDirectories):
                args += [
                    "-prop",
                    "OutputDirectory{}={}".format(index, outputDirectory)
                ]

        if dependencyIds:
            args += [
                "-prop",
                "JobDependencies="+",".join(dependencyIds)
            ]

        output = self.__executeDeadlineCommand(
            ' '.join([
                "deadlinecommand",
                self.__serializeDeadlineArgs(args, renderfarmJob.jobDirectory())
            ]),
        )

        jobIdPrefix = "JobID="
        jobId = list(filter(lambda x: x.startswith(jobIdPrefix), output.split("\n")))

        if jobId:
            # it should contain just a single job id
            return jobId[0][len(jobIdPrefix):]
        else:
            raise DeadlineCommandError(output)

    def __defaultJobArgs(self, command, jobDataFilePath):
        """
        Return a list containing the default job args that later are passed to deadlinecommand.
        """
        args = [
            "-SubmitCommandLineJob",
            "-executable",
            "upython",
            "-arguments",
            command,
            "-priority",
            self.option('priority'),
            "-prop",
            "OverrideJobFailureDetection=true",
            "-prop",
            "FailureDetectionJobErrors={}".format(self.option('jobFailRetryAttempts') + 1),
            "-prop",
            "IncludeEnvironment=true",
            "-prop",
            'BatchName={}'.format(self.option('label'))
        ]

        # adding optional options
        for optionName in ['group', 'pool', 'secondaryPool']:
            if self.option(optionName):
                args += [
                    "-prop",
                    "{}={}".format(
                        optionName.capitalize(),
                        self.option(optionName)
                    )
                ]

        return args

    def __serializeDeadlineArgs(self, args, directory):
        """
        Return a file path about the serialized args.
        """
        temporaryFile = tempfile.NamedTemporaryFile(
            mode='w',
            prefix=os.path.join(directory, "deadline_"),
            suffix='.txt',
            delete=False
        )
        temporaryFile.write('\n'.join(map(str, args)))
        temporaryFile.close()

        return temporaryFile.name

    def __executeDeadlineCommand(self, command):
        """
        Auxiliary method used to execute a deadline command.
        """
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.option('env')
        )

        # capturing the output
        output, error = process.communicate()

        if error:
            raise DeadlineCommandError(error.decode("utf-8"))

        return output.decode("utf-8")


# registering dispatcher
Deadline.register(
    'renderFarm',
    Deadline
)
