"""
Various utilities.
"""

from __future__ import print_function

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
        items = [(k, v) for (k, v) in self.items()]
        self.clear()
        self.update(sorted(items))


def bbdb_file(user=None):
    """
    Return the standard BBDB file of the specified user.
    If no user is given, default to the current user.

    This is the file referred to by the 'bbdb-file' variable in emacs.
    The most reliable way to get it is to ask emacs directly.
    """

    tag = "BBDB="
    cmd = "emacs --batch"

    if user:
        cmd += " --user " + user

    cmd += " --eval '(message \"%s%%s\" bbdb-file)' --kill" % tag

    try:
        text = subprocess.check_output(cmd, shell=True,
                                       stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return None

    for line in text.split("\n"):
        if line.startswith(tag):
            path = line.replace(tag, "").strip()
            return os.path.expanduser(path)

    return None


def anniversaries(rec):
    "Yield anniversaries for a record."

    def int_or_none(value):
        try:
            return int(value)
        except ValueError:
            return None

    value = rec.fields.get('anniversary', None)
    if value:
        for entry in value.split("\\n"):
            entry = entry.strip()
            if ' ' in entry:
                date, tag = entry.split(' ', 1)
            else:
                date = entry
                tag = 'birthday'

            date = map(int_or_none, date.split('-', 2))
            yield tag, date


def ordinal(num):
    "Return number + ordinal (e.g., 1st, 4th, 13th, etc)."

    if 10 <= num <= 20:
        tag = "th"
    else:
        tag = ('st', 'nd', 'rd', 'th')[min(num % 10, 4) - 1]

    return str(num) + tag


def quote(string):
    return '"' + string.replace('"', r'\"') + '"'


if __name__ == "__main__":
    for num in range(30):
        print(ordinal(num))
