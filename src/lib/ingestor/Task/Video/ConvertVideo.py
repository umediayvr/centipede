from ..Task import Task
import os
import subprocess

class ConvertVideo(Task):
    """
    Convert a video using ffmpeg.
    """

    __defaultVcodec = "h264"
    __defaultAcodec = "acc"

    def __init__(self, *args, **kwargs):
        """
        Create a convert video object.
        """
        super(ConvertVideo, self).__init__(*args, **kwargs)

        self.setOption('vcodec', self.__defaultVcodec)
        self.setOption('acodec', self.__defaultAcodec)

    def _perform(self):
        """
        Perform the task.
        """
        vcodec = self.option('vcodec')
        acodec = self.option('acodec')

        for pathCrawler in self.pathCrawlers():
            targetFilePath = self.filePath(pathCrawler)

            # creating any necessary directories
            parentDirectory = os.path.dirname(targetFilePath)
            if not os.path.exists(parentDirectory):
                os.makedirs(parentDirectory)

            # ffmpeg command
            ffmpegCommand = 'ffmpeg -loglevel error -i {input} -vcodec {vcodec} -acodec {acodec} {output}'.format(
                input=pathCrawler.var('filePath'),
                output=targetFilePath,
                vcodec=vcodec,
                acodec=acodec
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
