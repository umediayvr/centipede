# gaffer needs to be imported at top-most
import Gaffer

# now we can import centipede
import centipede

# running serialized task
centipede.TaskWrapper.Subprocess.runSerializedTask()
