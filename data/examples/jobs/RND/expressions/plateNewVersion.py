import os
import re
from centipede.TemplateProcedure import TemplateProcedure

def plateNewVersionTemplateProcedure(prefix, job, seq, shot, plateName):
    """
    Returns a new version for the plate.
    """
    plateLocation = "{prefix}/{job}/sequences/{seq}/{shot}/online/publish/elements/{plateName}".format(
        prefix=prefix,
        job=job,
        seq=seq,
        shot=shot,
        plateName=plateName
    )

    version = 0
    versionRegEx = "^v[0-9]{3}$"

    # finding the latest version
    if os.path.exists(plateLocation):
        for directory in os.listdir(plateLocation):
            if re.match(versionRegEx, directory):
                version = max(int(directory[1:]), version)

    return 'v' + str(version + 1).zfill(3)


# registering procedure
TemplateProcedure.register(
    'plateNewVersion',
    plateNewVersionTemplateProcedure
)
