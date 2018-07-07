# compatibility with python 2/3
try:
    basestring
except NameError:
    basestring = str

class ProcedureNotFoundError(Exception):
    """Procedure not found error."""

class Procedure(object):
    """
    Procedures are used to provide functions to the template engine.
    """

    __registered = {}

    @staticmethod
    def register(name, procedureCallable):
        """
        Register a procedureCallable as procedure.
        """
        assert hasattr(procedureCallable, '__call__'), \
            "Invalid callable!"

        Procedure.__registered[name] = procedureCallable

    @staticmethod
    def registeredNames():
        """
        Return a list of registered procedures.
        """
        return Procedure.__registered.keys()

    @staticmethod
    def run(procedureName, *args):
        """
        Run the procedure and return a value base on the args.
        """
        if procedureName not in Procedure.__registered:
            raise ProcedureNotFoundError(
                'Could not find procedure name: "{0}"'.format(
                    procedureName
                )
            )

        # executing procedure
        return str(Procedure.__registered[procedureName](*args))

    @staticmethod
    def parseRun(procedure):
        """
        Parse and run a procedure.

        A procedure must be a string describbing the procedure name
        as first token and the arguments that should be passed to it
        separated by space (aka bash), for instance:
            "myprocedure arg1 arg2"
            "sum 1 2"

        The arguments are always parsed as string, and they should be
        handled per procedure callable bases.
        """
        assert isinstance(procedure, basestring), \
            "Invalid procedure type!"

        cleanedProcedure = list(filter(
            lambda x: x != '', procedure.strip(" ").split(" ")
        ))

        procedureName = cleanedProcedure[0]
        procedureArgs = cleanedProcedure[1:]

        return Procedure.run(procedureName, *procedureArgs)
