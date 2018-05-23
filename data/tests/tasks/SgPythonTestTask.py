from ingestor.Task import Task

class SgPythonTestTask(Task):
    """
    Dummy task for testing SgPython subprocess.
    """

    def _perform(self):
        from ushotgun import Session
        sg = Session.get()
        sourceCrawler = self.pathCrawlers()[0]
        sourceCrawler.setVar("testVar", sg.base_url)
        return [sourceCrawler.clone()]


Task.register(
    'sgPythonTestTask',
    SgPythonTestTask
)
