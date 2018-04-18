import json
from ingestor.Dispatcher import Dispatcher
from ingestor.Crawler.Fs.Path import Path
from ingestor.TaskHolder import TaskHolder
import argparse

def __run(dataJsonFile):
    """
    Execute the taskHolder.
    """
    data = {}
    with open(dataJsonFile) as jsonFile:
        data = json.load(jsonFile)

    # loading task holder
    taskHolder = TaskHolder.createFromJson(data['taskHolder'])

    if data['jobType'] == "collapsed":

        # loading input crawlers
        crawlers = []
        for taskInputFilePath in data['taskInputFilePaths']:
            with open(taskInputFilePath) as jsonFile:
                serializedCrawlers = json.load(jsonFile)
                crawlers += list(map(lambda x: Path.createFromJson(x), serializedCrawlers))

        dispatcher = Dispatcher.createFromJson(data['dispatcher'])
        dispatcher.dispatch(
            taskHolder,
            crawlers
        )

    elif data['jobType'] == "expanded":
        outputCrawlers = taskHolder.run()

        # writing resulted crawlers
        with open(data['taskResultFilePath'], 'w') as jsonFile:
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

# executing it
if __name__ == "__main__":
    args = parser.parse_args()
    __run(args.data)
