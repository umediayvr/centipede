import datetime
from ..Procedure import Procedure

class _Datetime(object):
    """
    Basic datetime functions.
    """

    @staticmethod
    def yyyy():
        """
        Return the year formated by 4 digits.
        """
        return datetime.datetime.now().strftime("%Y")

    @staticmethod
    def yy():
        """
        Return the year formated by 2 digits.
        """
        return datetime.datetime.now().strftime("%y")

    @staticmethod
    def mm():
        """
        Return the month formated by 2 digits.
        """
        return datetime.datetime.now().strftime("%m")

    @staticmethod
    def dd():
        """
        Return the day formated by 2 digits.
        """
        return datetime.datetime.now().strftime("%d")

    @staticmethod
    def hour():
        """
        Return the hour formated by 2 digits (24 hours format).
        """
        return datetime.datetime.now().strftime("%H")

    @staticmethod
    def minute():
        """
        Return the minutes formated by 2 digits.
        """
        return datetime.datetime.now().strftime("%d")

    @staticmethod
    def second():
        """
        Return the seconds formated by 2 digits.
        """
        return datetime.datetime.now().strftime("%S")


# registering procedures
Procedure.register(
    'yyyy',
    _Datetime.yyyy
)

Procedure.register(
    'yy',
    _Datetime.yy
)

Procedure.register(
    'mm',
    _Datetime.mm
)

Procedure.register(
    'dd',
    _Datetime.dd
)

Procedure.register(
    'hour',
    _Datetime.hour
)

Procedure.register(
    'minute',
    _Datetime.minute
)

Procedure.register(
    'second',
    _Datetime.second
)
