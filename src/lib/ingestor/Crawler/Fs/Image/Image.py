from ..File import File

class Image(File):
    """
    Abstracted image path crawler.
    """

    def __init__(self, *args, **kwargs):
        """
        Create an image crawler.
        """
        super(Image, self).__init__(*args, **kwargs)

        # setting a video tag
        self.setVar('imageType', 'single')

        self.__computeImageSequence()

    def isSequence(self):
        """
        Return if path holder is holding a file that is part of a image sequence.
        """
        nameParts = self.pathHolder().baseName().split(".")
        return (len(nameParts) >= 3 and self.pathHolder().baseName().split(".")[-2].isdigit())

    def __computeImageSequence(self):
        """
        Compute the image sequence tags and vars.
        """
        if self.isSequence():
            nameParts = self.pathHolder().baseName().split(".")
            frame = nameParts[-2]

            self.setVar('imageType', 'sequence')
            self.setVar('name', '.'.join(nameParts[:-2]))
            self.setVar('frame', int(frame))
            self.setVar('padding', len(frame))

            # image sequence tag:
            # this information is used to group files, we don't necessary
            # need to obey the information about the padding from the file itself,
            # since the sequence can be unpadded.
            self.setTag(
                'imageSequence',
                '{0}.####.{1}'.format(
                    '.'.join(nameParts[:-2]),
                    nameParts[-1]
                )
            )
        else:
            self.setTag('image', self.pathHolder().baseName())
