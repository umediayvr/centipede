import json
import os
import sys
import ingestor

try:
    # collecting the files that should be processed by the ingestor
    files = []
    filesArg = sys.argv.index('-files')
    fileJsonFile = sys.argv[filesArg + 1]
    with open(fileJsonFile) as jsonFile:
    	files = json.load(jsonFile)

    # configuration path
    configPath = sys.argv[sys.argv.index('-configPath') + 1]

    # loading configuration
    taskHolderLoader = ingestor.TaskHolderLoader.JsonLoader()
    taskHolderLoader.addFromJsonDirectory(configPath)

    # getting crawlers based on the files
    crawlers = list(map(lambda x: ingestor.Crawler.Fs.Path.create(ingestor.PathHolder(x)), files))

    # running tasks
    for taskHolder in taskHolderLoader.taskHolders():
        taskHolder.run(crawlers)

finally:
    sys.exit(1)
