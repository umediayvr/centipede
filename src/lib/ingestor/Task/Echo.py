from .Task import Task

class Echo(Task):
    """
    Yields the target file path (for debugging purposes).
    """

    def _perform(self):
        """
        Perform the task.
        """
        for pathCrawler in self.pathCrawlers():
            yield pathCrawler

# registering task
Task.register(
    'echo',
    Echo
)
