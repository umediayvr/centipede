from .ExrRender import ExrRender

class ShotRender(ExrRender):
    """
    Custom crawler used to detect renders for shots.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a Render object.
        """
        super(ShotRender, self).__init__(*args, **kwargs)

        parts = self.var("name").split("_")

        self.setVar('job', parts[0])
        self.setVar('seq', parts[1])
        self.setVar('shot', parts[2])
        self.setVar('pipelineStep', parts[3])
        self.setVar('variant', parts[4])
        self.setVar('pass', parts[5])

# registering crawler
ShotRender.register(
    'shotRender',
    ShotRender
)
