import ingestor
import os

def clientStatusExpression(sg_status_list):
    """
    Return a nice name for our internal shotgun status.
    """
    # Sent for final
    if sg_status_list == "sff":
        return "Final"
    # Sent for review
    elif sg_status_list == "sfr":
        return "Work in Progress"
    else:
        return "Work in Progress"

def fileTypeExpression(filePath):
    """
    Return a nice name for the file type.
    """
    name, ext = os.path.splitext(filePath)
    if ext == ".mov":
        if name.endswith("_h264"):
            return "H264"
        elif name.endswith("_prores"):
            return "PRORES"
        else:
            return "DNxHD"
    elif ext == ".exr":
        return "EXR"
    else:
        return ext.upper().strip(".")


# registering expressions
ingestor.ExpressionEvaluator.register(
    'clientStatus',
    clientStatusExpression
)

ingestor.ExpressionEvaluator.register(
    'clientFileType',
    fileTypeExpression
)
