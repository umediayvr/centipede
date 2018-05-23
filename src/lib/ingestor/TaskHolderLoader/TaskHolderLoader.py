from ..TaskHolder import TaskHolder

class TaskHolderLoader(object):
    """
    Abstracted task holders loader.
    """

    def __init__(self):
        """
        Create a config loader.
        """
        self.__taskHolders = []

    def addTaskHolder(self, taskHolder):
        """
        Add a task holder to the config loader.
        """
        assert (isinstance(taskHolder, TaskHolder)), \
            "Invalid task holder object"

        self.__taskHolders.append(taskHolder)

    def taskHolders(self):
        """
        Return a list of task holders associated with the config loader.
        """
        return self.__taskHolders
