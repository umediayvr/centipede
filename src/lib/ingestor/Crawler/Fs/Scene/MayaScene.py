from .Scene import Scene

class MayaScene(Scene):
    """
    Crawler used to detect maya scenes.
    """

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains a Maya scene.
        """
        if not super(Scene, cls).test(pathHolder, parentCrawler):
            return False

        return pathHolder.ext() in ['ma', 'mb']

# registering crawler
MayaScene.register(
    'mayaScene',
    MayaScene
)
