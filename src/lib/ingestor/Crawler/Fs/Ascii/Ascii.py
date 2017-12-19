from ..File import File

class Ascii(File):
    """
    Abstracted ascii crawler.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a ascii crawler.
        """
        super(File, self).__init__(*args, **kwargs)
        self.__parsedContents = None

    def _runParser(self):
        """
        For re-implementation: Needs to return the parsed data.
        """
        f = open(self.var('filePath'), 'r')
        contents = f.read()
        f.close()
        return contents

    def contents(self):
        """
        Return the parsed contents.
        """
        if not self.__parsedContents:
            self.__parsedContents = self._runParser()

        return self.__parsedContents
