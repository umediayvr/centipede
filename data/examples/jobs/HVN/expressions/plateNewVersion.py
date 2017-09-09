import os
import re
import ingestor

def plateNewVersionExpression(prefix, seq, shot, plateName):
    """
    Returns a new version for the plate.
    """
    plateLocation = "{prefix}/060_Heaven/sequences/{seq}/{shot}/online/publish/elements/{plateName}".format(
        prefix=prefix,
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


# registering expression
ingestor.ExpressionEvaluator.register(
    'plateNewVersion',
    plateNewVersionExpression
)
