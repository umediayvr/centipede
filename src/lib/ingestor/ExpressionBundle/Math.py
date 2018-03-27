import operator
from ..ExpressionEvaluator import ExpressionEvaluator

class _Math(object):
    """
    Basic math functions.
    """

    @staticmethod
    def sumInt(*args):
        """
        Sum (cast to integer).
        """
        intArgs = _Math.__castToInt(*args)
        return int(operator.add(
            intArgs[0],
            intArgs[1]
        ))

    @staticmethod
    def subtractInt(*args):
        """
        Subtraction (cast to integer).
        """
        intArgs = _Math.__castToInt(*args)
        return int(operator.sub(
            intArgs[0],
            intArgs[1]
        ))

    @staticmethod
    def multiplyInt(*args):
        """
        Multiply (cast to integer).
        """
        intArgs = _Math.__castToInt(*args)
        return int(operator.mul(
            intArgs[0],
            intArgs[1]
        ))

    @staticmethod
    def divideInt(*args):
        """
        Divide (cast to integeselfr).
        """
        intArgs = _Math.__castToInt(*args)
        return int(operator.truediv(
            intArgs[0],
            intArgs[1]
        ))

    @staticmethod
    def minimumInt(*args):
        """
        Minimum (cast to integer).
        """
        intArgs = _Math.__castToInt(*args)
        return int(min(
            intArgs[0],
            intArgs[1]
        ))

    @staticmethod
    def maximumInt(*args):
        """
        Maximum (cast to integer).
        """
        intArgs = _Math.__castToInt(*args)
        return int(max(
            intArgs[0],
            intArgs[1]
        ))

    @staticmethod
    def __castToInt(*args):
        """
        Cast the input args to int.
        """
        return list(map(int, args))


# sum
ExpressionEvaluator.register(
    'sum',
    _Math.sumInt
)

# subtraction
ExpressionEvaluator.register(
    'sub',
    _Math.subtractInt
)

# multiply
ExpressionEvaluator.register(
    'mult',
    _Math.multiplyInt
)

# divide
ExpressionEvaluator.register(
    'div',
    _Math.divideInt
)

# minimum
ExpressionEvaluator.register(
    'min',
    _Math.minimumInt
)

# maximum
ExpressionEvaluator.register(
    'max',
    _Math.maximumInt
)
