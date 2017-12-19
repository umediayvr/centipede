import os
import re
import ingestor

def textureNewVersionExpression(versionsPath):
    """
    Return a new version for the texture.
    """
    version = 0
    versionRegEx = "^v[0-9]{3}$"

    # finding the latest version
    if os.path.exists(versionsPath):
        for directory in os.listdir(versionsPath):
            if re.match(versionRegEx, directory):
                version = max(int(directory[1:]), version)

    return 'v' + str(version + 1).zfill(3)


# registering expression
ingestor.ExpressionEvaluator.register(
    'textureNewVersion',
    textureNewVersionExpression
)
