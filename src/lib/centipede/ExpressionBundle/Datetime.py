import datetime
from ..ExpressionEvaluator import ExpressionEvaluator

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


# registering expressions
ExpressionEvaluator.register(
    'yyyy',
    _Datetime.yyyy
)

ExpressionEvaluator.register(
    'yy',
    _Datetime.yy
)

ExpressionEvaluator.register(
    'mm',
    _Datetime.mm
)

ExpressionEvaluator.register(
    'dd',
    _Datetime.dd
)

ExpressionEvaluator.register(
    'hour',
    _Datetime.hour
)

ExpressionEvaluator.register(
    'minute',
    _Datetime.minute
)

ExpressionEvaluator.register(
    'second',
    _Datetime.second
)
