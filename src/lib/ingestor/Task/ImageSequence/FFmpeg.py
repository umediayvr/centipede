import os
import subprocess
from ..Task import Task

class FFmpeg(Task):
    """
    Abstracted ffmpeg task.

    Required Options: sourceColorSpace, targetColorSpace and frameRate
    """
    __defaultScale = 1.0
    __defaultVideoCodec = "libx264"
    __defaultPixelFormat = "yuvj420p"
    __defaultBitRate = 115

    def __init__(self, *args, **kwargs):
        """
        Create a ffmpeg object.
        """
        super(FFmpeg, self).__init__(*args, **kwargs)

        self.setOption('scale', self.__defaultScale)
        self.setOption('videoCodec', self.__defaultVideoCodec)
        self.setOption('pixelFormat', self.__defaultPixelFormat)
        self.setOption('bitRate', self.__defaultBitRate)

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

        ffmpegCommand = 'ffmpeg -loglevel error -framerate {frameRate} -start_number {startFrame} -i "{inputSequence}" -framerate {frameRate} -vcodec {videoCodec} -b {bitRate}M -minrate {bitRate}M -maxrate {bitRate}M -color_primaries smpte170m -color_trc bt709 -color_primaries {targetColorSpace} -color_trc {sourceColorSpace} -colorspace {targetColorSpace} -pix_fmt {pixelFormat} {scale} -y "{output}"'.format(
            frameRate=self.option('frameRate'),
            startFrame=startFrame,
            videoCodec=self.option('videoCodec'),
            bitRate=self.option('bitRate'),
            pixelFormat=self.option('pixelFormat'),
            sourceColorSpace=self.option('sourceColorSpace'),
            targetColorSpace=self.option('targetColorSpace'),
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
