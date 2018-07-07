from ..Procedure import Procedure

class _Text(object):
    """
    Basic image sequence functions.
    """

    @staticmethod
    def upper(string):
        """
        Return string coverted to upper case.
        """
        return str(string).upper()

    @staticmethod
    def lower(string):
        """
        Return string coverted to lower case.
        """
        return str(string).lower()

    @staticmethod
    def replace(text, searchValue, replaceValue):
        """
        Return a string where all search value are replaced by the replace value.
        """
        return text.replace(searchValue, replaceValue)

    @staticmethod
    def remove(text, removeValue):
        """
        Return a string where all remove value are removed from the text.
        """
        return text.replace(removeValue, '')


# upper case
Procedure.register(
    'upper',
    _Text.upper
)

# lower case
Procedure.register(
    'lower',
    _Text.lower
)

# replace
Procedure.register(
    'replace',
    _Text.replace
)

# remove
Procedure.register(
    'remove',
    _Text.remove
)
