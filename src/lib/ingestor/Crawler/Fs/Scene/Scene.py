from ..File import File

class Scene(File):
    """
    Abstracted scene path crawler.
    """

    @classmethod
    def extensions(cls):
        """
        Return the list of available extensions, to be implemented by derived classes.
        """
        raise NotImplemented
