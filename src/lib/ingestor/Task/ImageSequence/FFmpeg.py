import os
import subprocess
from ..Task import Task

class FFmpeg(Task):
    """
    Abstracted ffmpeg task.
    """
    __defaultFrameRate = 24.0
    __defaultScale = 1.0
    __defaultVideoCodec = "libx264"
    __defaultBitRate = 115
    __defaultFilterGraph = "colormatrix=bt601:bt709"

    def __init__(self, *args, **kwargs):
        """
        Create a ffmpeg object.
        """
        super(FFmpeg, self).__init__(*args, **kwargs)

        self.setOption('frameRate', self.__defaultFrameRate)
        self.setOption('scale', self.__defaultScale)
        self.setOption('videoCodec', self.__defaultVideoCodec)
        self.setOption('bitRate', self.__defaultBitRate)
        self.setOption('filterGraph', self.__defaultFilterGraph)

    def executeFFmpeg(self, sequenceCrawlers, outputFilePath):
        """
        Executes ffmpeg.
        """
        crawler = sequenceCrawlers[0]
        startFrame = crawler.var('frame')
        padding = crawler.var('padding')

        inputSequence = os.path.join(
            os.path.dirname(crawler.var('filePath')),
            '{name}.%0{padding}d.{ext}'.format(
                name=crawler.var('name'),
                padding=crawler.var('padding'),
                ext=crawler.var('ext')
            )
        )

        # trying to create the directory automatically in case it does not exist
        try:
            os.makedirs(os.path.dirname(outputFilePath))
        except OSError:
            pass

        # adding options
        scale = ""
        if self.option('scale') != -1.0:
            scale = '-vf scale=iw*{0}:ih*{0}'.format(
                self.option('scale')
            )

        ffmpegCommand = 'ffmpeg -loglevel error -framerate {frameRate} -start_number {startFrame} -i "{inputSequence}" -framerate {frameRate} -vcodec {videoCodec} -b {bitRate}M -minrate {bitRate}M -maxrate {bitRate}M -vf {filterGraph} {scale} -y "{output}"'.format(
            frameRate=self.option('frameRate'),
            startFrame=startFrame,
            videoCodec=self.option('videoCodec'),
            bitRate=self.option('bitRate'),
            filterGraph=self.option('filterGraph'),
            inputSequence=inputSequence,
            scale=scale,
            output=outputFilePath
        )

        # calling ffmpeg
        process = subprocess.Popen(
            ffmpegCommand,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ,
            shell=True
        )

        # capturing the output
        output, error = process.communicate()

        # in case of any erros
        if error:
            raise Exception(error)
