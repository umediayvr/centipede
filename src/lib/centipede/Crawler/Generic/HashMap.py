from ..Crawler import Crawler

class HashMap(Crawler):
    """
    HashMap crawler to store key/value data in memory.
    """

    def __init__(self, data, parentCrawler=None):
        """
        Create a HashMap crawler.
        """
        super(HashMap, self).__init__(data, parentCrawler)
        self.setVar('data', data)
        self.__data = data

    def __getitem__(self, key):
        """
        Return the value stored in the data for the given key.
        """
        return self.__data[key]

    def __repr__(self):
        """
        Return a string representation of the crawler.
        """
        return repr(self.__data)

    def items(self):
        """
        Return the data in (key, value) pairs.
        """
        return self.__data.items()

    @classmethod
    def test(cls, data=None, parentCrawler=None):
        """
        Tests if the data is dictionary.
        """
        return isinstance(data, dict)


Crawler.register(
    'hashmap',
    HashMap
)
