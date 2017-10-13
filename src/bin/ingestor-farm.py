import json
import os
import sys
import ingestor

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

# loading overrides
overrides = {}
sourceOverridesConfig = os.path.join(configPath, "overrides", "source.json")
if os.path.exists(sourceOverridesConfig):
    with open(sourceOverridesConfig) as sourceFile:
        overrides = json.load(sourceFile)

# getting crawlers based on the files
crawlers = list(map(lambda x: ingestor.Crawler.Fs.Path.create(ingestor.PathHolder(x)), files))

# applying overrides to the crawler
if overrides:
    for crawler in crawlers:
        filePath = crawler.var('filePath')
        if filePath in overrides:
            # applying override to the crawler
            for varName, varValue in overrides[filePath].items():
                crawler.setVar(varName, varValue)

# running tasks
for taskHolder in taskHolderLoader.taskHolders():
    taskHolder.run(crawlers)
