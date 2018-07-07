import operator
from ..Procedure import Procedure

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
        Divide (cast to integer).
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
Procedure.register(
    'sum',
    _Math.sumInt
)

# subtraction
Procedure.register(
    'sub',
    _Math.subtractInt
)

# multiply
Procedure.register(
    'mult',
    _Math.multiplyInt
)

# divide
Procedure.register(
    'div',
    _Math.divideInt
)

# minimum
Procedure.register(
    'min',
    _Math.minimumInt
)

# maximum
Procedure.register(
    'max',
    _Math.maximumInt
)
