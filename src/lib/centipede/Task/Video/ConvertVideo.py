from ..Task import Task
import os
import subprocess

class ConvertVideo(Task):
    """
    Convert a video using ffmpeg.
    """

    __defaultVideoArgs = "-vcodec h264 -pix_fmt yuvj420p"
    __defaultAudioArgs = "-f lavfi -t 1 -i anullsrc=r=48000:cl=stereo -acodec aac"
    __defaultBitRate = 115

    def __init__(self, *args, **kwargs):
        """
        Create a convert video object.
        """
        super(ConvertVideo, self).__init__(*args, **kwargs)

        self.setOption('videoArgs', self.__defaultVideoArgs)
        self.setOption('audioArgs', self.__defaultAudioArgs)
        self.setOption('bitRate', self.__defaultBitRate)

    def _perform(self):
        """
        Perform the task.
        """
        videoArgs = self.option('videoArgs')
        audioArgs = self.option('audioArgs')
        bitRate = self.option('bitRate')

        for crawler in self.crawlers():
            targetFilePath = self.target(crawler)

            # creating any necessary directories
            parentDirectory = os.path.dirname(targetFilePath)
            if not os.path.exists(parentDirectory):
                os.makedirs(parentDirectory)

            # ffmpeg command
            ffmpegCommand = 'ffmpeg -loglevel error {audioArgs} -i {input} -b {bitRate}M -minrate {bitRate}M -maxrate {bitRate}M {videoArgs} -y {output}'.format(
                input=crawler.var('filePath'),
                output=targetFilePath,
                videoArgs=videoArgs,
                bitRate=bitRate,
                audioArgs=audioArgs
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
            output, errors = process.communicate()

            # in case of any erros
            if errors:
                raise Exception(errors)

        return super(ConvertVideo, self)._perform()


# registering task
Task.register(
    'convertVideo',
    ConvertVideo
)
