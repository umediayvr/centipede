from .ExrRender import ExrRender

class Turntable(ExrRender):
    """
    Custom crawler used to detect turntable renders.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a Turntable object.
        """
        super(Turntable, self).__init__(*args, **kwargs)

        parts = self.var("name").split("_")

        # Add the job var once job names on disk match job code names in shotgun
        # self.setVar('job', parts[0])
        self.setVar('assetName', parts[1])
        self.setVar('step', parts[2])
        self.setVar('variant', parts[3])
        self.setVar('pass', parts[4])

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a turntable.
        """
        if not super(Turntable, cls).test(pathHolder, parentCrawler):
            return False

        renderType = pathHolder.baseName().split(".")[0].split("_")[-1]

        return renderType == "turntable"


# registering crawler
Turntable.register(
    'turntable',
    Turntable
)
