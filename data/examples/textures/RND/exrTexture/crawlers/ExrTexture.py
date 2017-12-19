import ingestor

class ExrTexture(ingestor.Crawler.Fs.Image.Exr):
    """
    Custom crawler used to detect textures.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a Texture object.
        """
        super(ExrTexture, self).__init__(*args, **kwargs)
        parts = self.var("name").split("_")

        self.setVar("assetName", parts[0])
        self.setVar("mapType", parts[1].upper())
        self.setVar("udim", self.__parseUDIM(self.pathHolder()))

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains an texture  exr file.
        """
        if not super(ExrTexture, cls).test(pathHolder, parentCrawler):
            return False

        return (cls.__parseUDIM(pathHolder) is not None)

    @classmethod
    def __parseUDIM(cls, pathHolder):
        """
        Return an integer about the udim found in the texture name (or none).
        """
        name = pathHolder.baseName()[:-(len(pathHolder.ext()) + 1)]
        parts = name.split("_")

        if len(parts) >= 4 and parts[3].startswith("u") and parts[4].startswith("v"):
            print(parts)

        udim = None
        if len(parts) >= 3:
            # detecting based on mari UDIM:
            # http://bneall.blogspot.ca/p/udim-guide.html
            # assetName_textureType_1001.exr
            if parts[2].isdigit() and len(parts[2]) == 4:
                udim = int(parts[2])

            # detecting based on mudbox:
            # assetName_textureType_u1_v1.exr (starts from 1)
            elif len(parts) >= 4 and parts[2].startswith("u") and parts[3].startswith("v"):
                u = int(parts[2][1:]) - 1
                v = int(parts[3][1:]) - 1
                udim = 1000 + (u + 1) + (v * 10)
        return udim


# registering crawler
ExrTexture.register(
    'exrTexture',
    ExrTexture
)
