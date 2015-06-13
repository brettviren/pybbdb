"""
Various utilities.
"""

from collections import OrderedDict
from functools import total_ordering


@total_ordering
class SortedDict(OrderedDict):
    """
    An ordered dictionary which allows sorting of keys in-place.
    """

    def __init__(self, *args, **kw):
        super(SortedDict, self).__init__(*args, **kw)

    def __lt__(self, other):
        return list(self.items()) < list(other.items())

    def sort(self):
        items = self.items()
        self.clear()
        self.update(sorted(items))


def quote(string):
    return '"' + string.replace('"', r'\"') + '"'
