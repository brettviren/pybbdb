"""
Convert BBDB events to iCalendar format.

Requires:
   vobject -- https://pypi.python.org/pypi/vobject
"""

import vobject
import datetime as dt
from bbdb.utils import anniversaries, ordinal


def calendar(db, calyear=None):
    """
    Create an iCalendar from a BBDB database.
    """

    if not calyear:
        calyear = dt.datetime.now().year

    cal = vobject.iCalendar()

    for rec in db.records:
        for tag, (year, month, day) in anniversaries(rec):
            event = cal.add('vevent')
            if year and year > calyear:
                continue

            if tag.startswith('birth'):
                tag = 'birthday' if calyear != year else 'born'
            else:
                tag = tag.strip()
                if calyear != year:
                    tag += ' anniversary'

            if year and year != calyear:
                tag = ordinal(calyear - year) + " " + tag

            start = event.add('dtstart')
            start.value_param = 'DATE'
            start.value = dt.datetime(calyear, month, day)

            summary = event.add('summary')
            summary.value = rec.name + "'s " + tag

    return cal


if __name__ == "__main__":
    from bbdb.database import readdb

    db = readdb()
    cal = calendar(db, 2012)
    print cal.serialize()
