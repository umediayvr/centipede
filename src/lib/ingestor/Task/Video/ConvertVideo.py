from ..Task import Task
import os
import subprocess

class ConvertVideo(Task):
    """
    Convert a video using ffmepg.
    """

    __defaultVcodec = "h264"
    __defaultAcodec = "acc"

    def __init__(self, *args, **kwargs):
        """
        Create a convert video object.
        """
        super(ConvertVideo, self).__init__(*args, **kwargs)

        self.setOption('vcoded', self.__defaultVcodec)
        self.setOption('acodec', self.__defaultAcodec)

    def _perform(self):
        """
        Perform the task.
        """
        vcoded = self.option('vcoded')
        acodec = self.option('acodec')

        for pathCrawler in self.pathCrawlers():
            targetFilePath = self.filePath(pathCrawler)

            # ffmpeg command
            ffmpegCommand = 'ffmpeg -loglevel error -i {input} -vcodec {vcodec} -acodec {acodec} {output}'.format(
                input=pathCrawler.var('filePath'),
                output=targetFilePath,
                vcodec=vcoded,
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
            output, error = process.communicate()

            # in case of any erros
            if error:
                raise Exception(error)

        return super(ConvertVideo, self)._perform()


# registering task
Task.register(
    'convertVideo',
    ConvertVideo
)
