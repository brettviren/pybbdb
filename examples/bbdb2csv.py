"""
Convert BBDB entries into CSV format.
"""

import sys
import csv


def dictaddr(rec):
    return {key: value.description for key, value in rec.address.items()}


def dictlist(data, sep=", ", remove="()"):
    entries = []
    num = len(data)
    for key, value in data.items():
        if num > 1:
            value = "%s: %s" % (key, value)

        for char in remove:
            value = value.replace(char, "")

        entries.append(value)

    return sep.join(entries)


if __name__ == "__main__":
    from bbdb.database import readdb

    db = readdb()
    writer = csv.writer(sys.stdout)
    writer.writerow(['Name', 'Address', 'Phone'])

    for rec in db.records:
        if rec.address or rec.phone:
            writer.writerow([rec.name,
                             dictlist(dictaddr(rec)),
                             dictlist(rec.phone)])
