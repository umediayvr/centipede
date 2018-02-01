import os
from ..Task import Task
from .NukeScript import NukeScript

class NukeTemplate(NukeScript):
    """
    Executes a nuke scene by triggering the write nodes.

    Required options: template (full path of the nuke scene)

    Please checkout the base class for further information about the options.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a nuke template task.
        """
        super(NukeTemplate, self).__init__(*args, **kwargs)

        self.setOption(
            'script',
            os.path.join(
                os.path.dirname(
                    os.path.realpath(__file__)
                ),
                "aux",
                "loadTemplate.py"
            )
        )


# registering task
Task.register(
    'nukeTemplate',
    NukeTemplate
)
