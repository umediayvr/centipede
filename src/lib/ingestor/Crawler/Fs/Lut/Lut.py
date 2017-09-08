from ..File import File

class Lut(File):
    """
    Abstracted lut path crawler.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a lut crawler.
        """
        super(Lut, self).__init__(*args, **kwargs)

        # setting a lut tag
        self.setTag(
            'lut',
            self.pathHolder().baseName()
        )
