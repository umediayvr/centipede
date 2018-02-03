import subprocess
import os
import json
from ..File import File

class Video(File):
    """
    Abstracted video path crawler.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a video crawler.
        """
        super(Video, self).__init__(*args, **kwargs)

        self.setVar('category', 'video')

        # setting a video tag
        self.setTag(
            'video',
            self.pathHolder().baseName()
        )

        # Get width and height from movie using ffprobe
        cmd = 'ffprobe -v quiet -print_format json -show_entries stream=height,width {}'.format(self.var('filePath'))

        # calling ffmpeg
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
        self.setVar('width', result['streams'][0]['width'])
        self.setVar('height', result['streams'][0]['height'])
