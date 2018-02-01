from .ExrRender import ExrRender

class TkRender(ExrRender):
    """
    Custom crawler to parse information from a toolkit render.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a TkRender object.
        """
        super(TkRender, self).__init__(*args, **kwargs)

        parts = self.var("name").split("_")
        locationParts = parts[0].split("-")

        # Add the job var once job names on disk match job code names in shotgun
        # self.setVar('job', locationParts[0])
        self.setVar('seq', locationParts[1])
        self.setVar('shot', '-'.join(locationParts))
        self.setVar('versionName', parts[-2])
        self.setVar('version', int(parts[-2][1:]))

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a shotgun nuke render.
        """
        if not super(TkRender, cls).test(pathHolder, parentCrawler):
            return False

        renderType = pathHolder.baseName().split(".")[0].split("_")[-1]

        return renderType == "tk"


# registering crawler
TkRender.register(
    'tkRender',
    TkRender
)
