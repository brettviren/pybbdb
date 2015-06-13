"""
Various utilities.
"""

import os
import subprocess

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


def bbdb_file(user=None):
    """
    Return the standard BBDB file of the specified user.
    If no user is given, default to the current user.

    This is the file referred to by the 'bbdb-file' variable in emacs.
    The most reliable way to get it is to ask emacs directly.
    """

    if not user:
        user = os.environ["USER"]

    tag = "BBDB="
    cmd = "emacs --batch --user " + user
    cmd += " --eval '(message \"%s%%s\" bbdb-file)' --kill" % tag

    text = subprocess.check_output(cmd, shell=True,
                                   stderr=subprocess.STDOUT)

    for line in text.split("\n"):
        if line.startswith(tag):
            path = line.replace(tag, "").strip()
            return os.path.expanduser(path)

    return None


def quote(string):
    return '"' + string.replace('"', r'\"') + '"'


if __name__ == "__main__":
    print bbdb_file()
