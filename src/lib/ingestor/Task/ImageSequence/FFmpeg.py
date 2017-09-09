import os
import tempfile
import subprocess
from ..Task import Task

class FFmpeg(Task):
    """
    Abstracted ffmpeg task.
    """
    __defaultFrameRate = 24.0
    __defaultScale = 1.0

    def __init__(self, *args, **kwargs):
        """
        Create a ffmpeg object.
        """
        super(FFmpeg, self).__init__(*args, **kwargs)

        self.setOption('frameRate', self.__defaultFrameRate)
        self.setOption('scale', self.__defaultScale)

    def executeFFmpeg(self, imageFilePaths, outputFilePath):
        """
        Executes ffmpeg.
        """
        # generating a temporary file that is going to contain the frames
        # that should be processed by ffmpeg
        tempSequenceFile = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".txt",
            mode='w'
        )

        # writting a temporary file that contains the image file paths
        fileEntries = '\n'.join(map(lambda x: "file '{0}'".format(x), imageFilePaths))
        tempSequenceFile.write(fileEntries)

        # trying to create the directory automatically in case it does not exist
        try:
            os.makedirs(os.path.dirname(outputFilePath))
        except OSError:
            pass

        frameRate = '-r {0}'.format(self.option('frameRate'))
        scale = ""

        # adding options
        if self.option('scale') != -1.0:
            scale = '-vf scale=iw*{0}:ih*{0}'.format(
                self.option('scale')
            )

        # calling ffmpeg
        process = subprocess.Popen(
            'ffmpeg {frameRate} -y -loglevel quiet -f concat -safe 0 -i "{input}" {scale} "{output}"'.format(
                frameRate=frameRate,
                input=tempSequenceFile.name,
                scale=scale,
                output=outputFilePath
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ,
            shell=True
        )

        # capturing the output
        output, error = process.communicate()

        # removing the temporary file
        os.unlink(tempSequenceFile.name)

        # in case of any erros
        if error:
            raise Exception(error)
