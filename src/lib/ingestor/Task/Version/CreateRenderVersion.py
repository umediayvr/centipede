import os
from ...Crawler.Fs import Path
from ...Crawler.Fs.Scene import Scene
from ..Task import Task
from .CreateIncrementalVersion import CreateIncrementalVersion

class CreateRenderVersion(CreateIncrementalVersion):
    """
    Create texture version task.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a render version.
        """
        super(CreateRenderVersion, self).__init__(*args, **kwargs)

    def _perform(self):
        """
        Perform the task.
        """
        sourceScenes = set()

        for pathCrawler in self.pathCrawlers():

            targetFile = self.__computeRenderTargetLocation(pathCrawler)
            # copying the render file
            self.copyFile(pathCrawler.var('filePath'), targetFile)
            self.addFile(targetFile)

            # Crawl from source directory for scenes to save along with data
            pathCrawler = Path.createFromPath(pathCrawler.var('sourceDirectory'))
            sceneCrawlers = pathCrawler.glob([Scene])
            for sceneCrawler in sceneCrawlers:
                sourceScenes.add(sceneCrawler.var('filePath'))

        # Copy source scenes
        for sourceScene in sourceScenes:
            targetScene = os.path.join(self.dataPath(), os.path.basename(sourceScene))
            self.copyFile(sourceScene, targetScene)
            self.addFile(targetScene)

        # Exclude all work scenes from incremental versioning
        exclude = set()
        for sceneClasses in Path.registeredSubclasses(Scene):
            exclude.update(sceneClasses.extensions())

        return super(CreateRenderVersion, self)._perform(incrementalExcludeTypes=list(exclude))

    def __computeRenderTargetLocation(self, crawler):
        """
        Compute the target file path for a render.
        """
        return os.path.join(
            self.dataPath(),
            "renders",
            "{}_{}_{}_{}_{}_{}.{}.{}".format(
                crawler.var('job'),
                crawler.var('seq'),
                crawler.var('shot'),
                crawler.var('step'),
                crawler.var('pass'),
                crawler.var('versionName'),
                str(crawler.var('frame')).zfill(crawler.var('padding')),
                crawler.var('ext')
            )
        )


# registering task
Task.register(
    'createRenderVersion',
    CreateRenderVersion
)
