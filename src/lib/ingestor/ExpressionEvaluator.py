class ExpressionNotFoundError(Exception):
    """Expression not found error."""

class ExpressionEvaluator(object):
    """
    Runs exressions used by templates.
    """

    __registered = {}

    @staticmethod
    def register(name, expressionCallable):
        """
        Register a expressionCallable as expression.
        """
        assert hasattr(expressionCallable, '__call__'), \
            "Invalid callable!"

        ExpressionEvaluator.__registered[name] = expressionCallable

    @staticmethod
    def registeredNames():
        """
        Return a list of registered expressions.
        """
        return ExpressionEvaluator.__registered.keys()

    @staticmethod
    def run(expressionName, *args):
        """
        Run the expression and return a value base on the args.
        """
        if expressionName not in ExpressionEvaluator.__registered:
            raise ExpressionNotFoundError(
                'Could not find expression name: "{0}"'.format(
                    expressionName
                )
            )

        # executing expression
        return str(ExpressionEvaluator.__registered[expressionName](*args))

    @staticmethod
    def parseRun(expression):
        """
        Parse and run an expression.

        An expression must be a string describbing the expression name
        as first token and the arguments that should be passed to it
        separated by space (aka bash), for instance:
            "myexpression arg1 arg2"
            "sum 1 2"

        The arguments are always parsed as string, and they should be
        handled per expression callable bases.
        """
        assert isinstance(expression, str), \
            "Invalid expression type!"

        cleanedExpressionEvaluator = list(filter(
            lambda x: x != '', expression.strip(" ").split(" ")
        ))

        expressionName = cleanedExpressionEvaluator[0]
        expressionArgs = cleanedExpressionEvaluator[1:]

        return ExpressionEvaluator.run(expressionName, *expressionArgs)
