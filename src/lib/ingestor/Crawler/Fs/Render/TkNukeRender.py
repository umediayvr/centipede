from .TkRender import TkRender

class TkNukeRender(TkRender):
    """
    Custom crawler to parse information from a toolkit render from nuke.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a TkNukeRender object.
        """
        super(TkNukeRender, self).__init__(*args, **kwargs)

        parts = self.var("name").split("_")
        self.setVar('step', parts[-5])
        self.setVar('renderName', parts[-4])
        self.setVar('output', parts[-3])


# registering crawler
TkNukeRender.register(
    'tkNukeRender',
    TkNukeRender
)
