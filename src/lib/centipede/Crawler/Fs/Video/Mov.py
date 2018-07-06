from .Video import Video
import subprocess
import json
import os

class Mov(Video):
    """
    Mov crawler.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a Mov crawler.
        """
        super(Mov, self).__init__(*args, **kwargs)

        self.__getFirstLastFrames()

    def __getFirstLastFrames(self):
        """
        Query first frame and last frame using ffprobe and set them as crawler variables if available.
        """
        cmd = 'ffprobe -v quiet -show_streams -print_format json {}'.format(self.var('filePath'))

        # calling ffprobe
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ,
            shell=True
        )

        # capturing the output
        output, error = process.communicate()
        result = json.loads(output.decode("utf-8"))
        if "streams" not in result:
            return

        tags = result['streams'][0].get("tags")
        if not tags:
            return

        startTimecode = tags.get("timecode")
        if not startTimecode:
            return

        nbFrames = int(result['streams'][0]['nb_frames'])-1
        frameRateStr = result['streams'][0]['avg_frame_rate'].split("/")
        frameRate = int(float(frameRateStr[0])/float(frameRateStr[1]))
        firstFrame = 0
        for f, t in zip((3600*frameRate, 60*frameRate, frameRate, 1), startTimecode.split(':')):
            firstFrame += f * int(t)
        self.setVar('firstFrame', firstFrame)
        self.setVar('lastFrame', firstFrame+nbFrames)

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a mov file.
        """
        if not super(Mov, cls).test(pathHolder, parentCrawler):
            return False

        return pathHolder.ext() == 'mov'


# registration
Mov.register(
    'mov',
    Mov
)
