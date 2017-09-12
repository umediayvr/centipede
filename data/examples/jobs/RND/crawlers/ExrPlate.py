import ingestor

class ExrPlate(ingestor.Crawler.Fs.Image.Exr):
    """
    Custom crawler to read production exr plates.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a ExrPlate object.
        """
        super(ExrPlate, self).__init__(*args, **kwargs)

        parts = self.var('name').split('_')
        locationParts = parts[0].split("-")
        plateParts = parts[1:]

        self.setVar('seq', locationParts[1])
        self.setVar('shot', '-'.join(locationParts))

        self.setVar('plateName', plateParts[0])
        self.setVar('version', int(plateParts[1][1:]))


# registering crawler
ExrPlate.register(
    'exrPlate',
    ExrPlate
)
