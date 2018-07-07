from ..Procedure import Procedure

class _ImageSequence(object):
    """
    Basic image sequence functions.
    """

    @staticmethod
    def padding(frame, size):
        """
        Return the frame with the padding size specified.
        """
        return str(int(frame)).zfill(int(size))

    @staticmethod
    def retimePadding(frame, retime, size):
        """
        Return the frame with the padding size specified.
        """
        return str(int(frame) + int(retime)).zfill(int(size))


# frame padding
Procedure.register(
    'pad',
    _ImageSequence.padding
)

# retime frame padding
Procedure.register(
    'retimepad',
    _ImageSequence.retimePadding
)
