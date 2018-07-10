import datetime
from ..TemplateProcedure import TemplateProcedure

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


# registering template procedures
TemplateProcedure.register(
    'yyyy',
    _Datetime.yyyy
)

TemplateProcedure.register(
    'yy',
    _Datetime.yy
)

TemplateProcedure.register(
    'mm',
    _Datetime.mm
)

TemplateProcedure.register(
    'dd',
    _Datetime.dd
)

TemplateProcedure.register(
    'hour',
    _Datetime.hour
)

TemplateProcedure.register(
    'minute',
    _Datetime.minute
)

TemplateProcedure.register(
    'second',
    _Datetime.second
)
