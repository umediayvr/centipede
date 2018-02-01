import nuke

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
for writeNode in nuke.allNodes('Write'):
    nuke.execute(writeNode, int(writeNode['first'].value()), int(writeNode['last'].value()))
