from .ExrRender import ExrRender

class Turntable(ExrRender):
    """
    Custom crawler used to detect turntable renders.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a Render object.
        """
        super(Turntable, self).__init__(*args, **kwargs)

        parts = self.var("name").split("_")

        self.setVar('job', parts[0])
        self.setVar('assetName', parts[1])
        self.setVar('pipelineStep', parts[2])
        self.setVar('variant', parts[3])
        self.setVar('pass', parts[4])


# registering crawler
Turntable.register(
    'turntable',
    Turntable
)
