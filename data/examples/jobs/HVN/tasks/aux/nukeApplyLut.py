import nuke
import os

# reading options from the task.
# sequence, startFrame and endFrame are added automatically as options by
# the centipede, everthing else comes from the taskOptions
sequence = options['sequence']
lut = options['lut']
startFrame = options['startFrame']
endFrame = options['endFrame']
colorSpace = options['colorSpace']

# setting up nuke
nuke.root()['first_frame'].setValue(startFrame - 1)
nuke.root()['last_frame'].setValue(endFrame)

# creating a read node
read = nuke.nodes.Read(file=sequence)
read['first'].setValue(startFrame)
read['last'].setValue(endFrame)

# color transformations
colorTransform = nuke.nodes.OCIOFileTransform()
colorTransform['file'].setValue(lut)
colorTransform['working_space'].setValue(colorSpace)

# write node
ext = os.path.splitext(sequence)[-1][1:]
write = nuke.nodes.Write(file=sequence)
write['file_type'].setValue(ext)
write['colorspace'].setValue(colorSpace)

# rendering with all the original metadata
write['metadata'].setValue(4)

# adding the lut information to the header
metadata = nuke.createNode("ModifyMetaData", "metadata {{set {key} {value}}}".format(
    key="centipede:lut",
    value=lut
))

#set up inputs
colorTransform.setInput(0, read)
metadata.setInput(0, colorTransform)
write.setInput(0, metadata)

# writing the color transformed sequence
nuke.execute(write, startFrame - 1, endFrame)
