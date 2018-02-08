from .Image import Image
import subprocess
import os
import json

try:
    import OpenImageIO
except ImportError:
    hasOpenImageIO = False
else:
    hasOpenImageIO = True

class OiioReadFileError(Exception):
    """Oiio Read File Error."""

class Oiio(Image):
    """
    Open image io crawler.
    """

    def var(self, name):
        """
        Return var value using lazy loading implementation for width and height.
        """
        if name in ['width', 'height'] and name not in self.varNames():
            # alternatively width and height information could come from the
            # parent directory crawler "1920x1080". For more details take a look
            # at "Directory" crawler.
            if hasOpenImageIO:
                imageInput = OpenImageIO.ImageInput.open(self.pathHolder().path())

                # making sure the image has been successfully loaded
                if imageInput is None:
                    raise OiioReadFileError(
                        "Can't read information from file:\n{}".format(
                                self.pathHolder().path()
                            )
                        )

                spec = imageInput.spec()
                self.setVar('width', spec.width)
                self.setVar('height', spec.height)
                imageInput.close()
            else:
                self.__getWidthHeight()

        return super(Oiio, self).var(name)

    def __getWidthHeight(self):
        """
        Query width and height using ffprobe and set them as crawler variables.
        """
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
