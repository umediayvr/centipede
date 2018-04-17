from .RenderfarmJob import RenderfarmJob
from .ExpandedJob import ExpandedJob

class CollapsedJob(RenderfarmJob):
    """
    Implements a collapsed render farm job.

    A collapsed render farm job is used to await for the completion of expanded jobs.
    Then spawn a job with the result of the expanded jobs.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a render farm collapsed job object.
        """
        super(CollapsedJob, self).__init__(*args, **kwargs)

        self.__expandedJobs = []

    def addExpandedJob(self, expandedJob):
        """
        Add a resolved job as input of the unresolved job.
        """
        assert isinstance(expandedJob, ExpandedJob), \
            "Invalid ExpandedJob type!"

        self.__expandedJobs.append(expandedJob)

    def expandedJobs(self):
        """
        Return a list of file paths used related with serialized crawlers.
        """
        return self.__expandedJobs
