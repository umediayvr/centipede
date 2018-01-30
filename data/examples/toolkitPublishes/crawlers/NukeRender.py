import ingestor

class NukeRender(ingestor.Crawler.Fs.Image.Exr):
    """
    Custom crawler to read Nuke renders when using Shotgun Toolkit.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a NukeRender object.
        """
        super(NukeRender, self).__init__(*args, **kwargs)

        parts = self.var('sourceDirectory').split("/")

        self.setVar('seq', parts[5])
        self.setVar('shot', parts[6])
        self.setVar('renderName', parts[10])
        self.setVar('output', parts[11])
        self.setVar('versionName', parts[12])
        self.setVar('version', parts[12].split('v')[-1])
        self.setVar('width', int(parts[13].split('x')[0]))
        self.setVar('height', int(parts[13].split('x')[1]))


# registering crawler
NukeRender.register(
    'nukeRender',
    NukeRender
)
