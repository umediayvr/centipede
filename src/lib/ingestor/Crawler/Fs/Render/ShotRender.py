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

        # Add the job var once job names on disk match job code names in shotgun
        self.setVar('job', parts[0])
        self.setVar('seq', parts[1])
        self.setVar('shot', parts[2])
        self.setVar('step', parts[3])
        self.setVar('pass', parts[4])
        self.setVar('renderName', '{}-{}'.format(
            self.var('step'),
            self.var('pass')
            ),
            True
        )

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a shot render.
        """
        if not super(ShotRender, cls).test(pathHolder, parentCrawler):
            return False

        renderType = pathHolder.baseName().split(".")[0].split("_")[-1]

        return renderType == "sr"


# registering crawler
ShotRender.register(
    'shotRender',
    ShotRender
)
