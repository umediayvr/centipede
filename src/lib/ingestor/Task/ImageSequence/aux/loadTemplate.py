import nuke
import json
import StringIO

# reading options from the task.
# sourceSequence, targetSequence, startFrame and endFrame are added automatically as options by
# the ingestor, everthing else comes from the taskOptions
sourceSequence = options['sourceSequence']
targetSequence = options['targetSequence']
startFrame = options['startFrame']
endFrame = options['endFrame']

nuke.scriptOpen(options['template'])

# setting up nuke
nuke.root()['first_frame'].setValue(startFrame)
nuke.root()['last_frame'].setValue(endFrame)

# executing the write node
createdFiles = []
for writeNode in nuke.allNodes('Write'):

    # skipping disabled write nodes
    if writeNode['disable'].value():
        continue

    nuke.execute(writeNode, int(writeNode['first'].value()), int(writeNode['last'].value()))

    # multiple files (image sequence)
    currentFile = writeNode['file'].getValue()
    if "%0" in currentFile:
        for frame in range(writeNode['first'].value(), int(writeNode['last'].value())):
            bufferString = StringIO.StringIO()
            bufferString.write(currentFile % frame)

            createdFiles.append(bufferString.getvalue())

    # single file
    else:
        createdFiles.append(currentFile)

# writting a json file with a list about all files created by the render
with open(options['_renderOutputData'], 'w') as output:
    json.dump(createdFiles, output)
