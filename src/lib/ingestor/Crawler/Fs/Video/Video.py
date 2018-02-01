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

        self.setVar('category', 'video')

        # setting a video tag
        self.setTag(
            'video',
            self.pathHolder().baseName()
        )
