from ..Task import Task
import os
import subprocess

class ConvertVideo(Task):
    """
    Convert a video using ffmpeg.
    """

    __defaultVideoArgs = "-vcodec h264"
    __defaultAudioArgs = "-f lavfi -t 1 -i anullsrc=r=48000:cl=stereo -acodec aac"

    def __init__(self, *args, **kwargs):
        """
        Create a convert video object.
        """
        super(ConvertVideo, self).__init__(*args, **kwargs)

        self.setOption('videoArgs', self.__defaultVideoArgs)
        self.setOption('audioArgs', self.__defaultAudioArgs)

    def _perform(self):
        """
        Perform the task.
        """
        videoArgs = self.option('videoArgs')
        audioArgs = self.option('audioArgs')

        for pathCrawler in self.pathCrawlers():
            targetFilePath = self.filePath(pathCrawler)

            # creating any necessary directories
            parentDirectory = os.path.dirname(targetFilePath)
            if not os.path.exists(parentDirectory):
                os.makedirs(parentDirectory)

            # ffmpeg command
            ffmpegCommand = 'ffmpeg -loglevel error -i {input} {videoArgs} {audioArgs} -y {output}'.format(
                input=pathCrawler.var('filePath'),
                output=targetFilePath,
                videoArgs=videoArgs,
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
