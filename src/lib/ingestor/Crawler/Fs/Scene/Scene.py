from ..File import File

class Scene(File):
    """
    Abstracted scene path crawler.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a scene crawler.
        """
        super(Scene, self).__init__(*args, **kwargs)

    @classmethod
    def extensions(cls):
        """
        Return the list of available extensions, to be implemented by derived classes.
        """
        raise NotImplemented
