from ..File import File

class Video(File):
    """
    Abstracted video path crawler.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a video crawler.
        """
        super(Video, self).__init__(*args, **kwargs)

        # setting a video tag
        self.setTag(
            'video',
            self.pathHolder().baseName()
        )
