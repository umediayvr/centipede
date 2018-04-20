import os
import json
from glob import glob
from collections import OrderedDict
from ingestor.Dispatcher import Dispatcher
from ingestor.Crawler.Fs.Path import Path
from ingestor.TaskHolder import TaskHolder
import argparse

def __run(dataJsonFile, rangeStart=None, rangeEnd=None):
    """
    Execute the taskHolder.
    """
    data = {}
    with open(dataJsonFile) as jsonFile:
        data = json.load(jsonFile)

    # loading task holder
    taskHolder = TaskHolder.createFromJson(data['taskHolder'])

    if data['jobType'] == "collapsed":
        taskInputFilePaths = []

        # looking for a task that has been chunkfied on the farm
        if len(data['taskInputFilePaths']) == 1 and not os.path.exists(data['taskInputFilePaths'][0]):
            nameParts = os.path.splitext(data['taskInputFilePaths'][0])

            taskInputFilePaths = glob(
                "{}_range_*_*.{ext}".format(nameParts[0], ext=nameParts[1][1:])
            )

            # since the range is padded by sorting them it is going to
            # provide the proper order that the crawlers should be loaded
            taskInputFilePaths.sort()
        else:
            taskInputFilePaths = data['taskInputFilePaths']

        # loading input crawlers
        crawlers = []
        for taskInputFilePath in taskInputFilePaths:
            with open(taskInputFilePath) as jsonFile:
                serializedCrawlers = json.load(jsonFile)
                crawlers += list(map(lambda x: Path.createFromJson(x), serializedCrawlers))

        dispatcher = Dispatcher.createFromJson(data['dispatcher'])
        dispatcher.dispatch(
            taskHolder,
            crawlers
        )

    elif data['jobType'] == "expanded":

        taskResultFilePath = data['taskResultFilePath']

        # in case the range has been specified
        if rangeStart is not None:

            # since a range has been assigned we need to modify the result file name
            # to include the range information. This can only done at this point
            # since execute-renderfarm is called directly by the renderfarm
            # manager itself to split the job in chunks (when chunkifyOnTheFarm
            # option is enabled in the dispatcher)
            nameParts = os.path.splitext(taskResultFilePath)
            taskResultFilePath = "{}_range_{}_{}.{ext}".format(
                nameParts[0],
                str(rangeStart).zfill(10),
                str(rangeEnd).zfill(10),
                ext=nameParts[1][1:]
            )

            # collecting all crawlers so we can re-assign only the ones that belong
            # to the range
            task = taskHolder.task()
            pathCrawlers = OrderedDict()
            for crawler in task.pathCrawlers():
                pathCrawlers[crawler] = task.filePath(crawler)

            # including only the crawlers from the specific range
            task.clear()
            for crawler in list(pathCrawlers.keys())[rangeStart: rangeEnd + 1]:
                filePath = pathCrawlers[crawler]
                task.add(
                    crawler,
                    filePath
                )

        outputCrawlers = taskHolder.run()

        # writing resulted crawlers
        with open(taskResultFilePath, 'w') as jsonFile:
            data = list(map(lambda x: x.toJson(), outputCrawlers))
            json.dump(
                data,
                jsonFile,
                indent=4
            )

    else:
        raise Exception(
            "Invalid execution type: {}".format(data['jobType'])
        )


# command-line interface
parser = argparse.ArgumentParser()

parser.add_argument(
    'data',
    metavar='data',
    type=str,
    help='json file containing the data that should be executed'
)

parser.add_argument(
    '--range-start',
    type=int,
    action="store",
    help='In case the task has been chunkfied on the farm, tells the context about the start crawler index'
)

parser.add_argument(
    '--range-end',
    type=int,
    action="store",
    help='In case the task has been chunkfied on the farm, tells the context about the end crawler index'
)

# executing it
if __name__ == "__main__":
    args = parser.parse_args()

    __run(
        args.data,
        args.range_start,
        args.range_end
    )
