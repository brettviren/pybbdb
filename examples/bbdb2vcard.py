"""
Convert BBDB entries to vCard format.

Requires:
   vobject -- https://pypi.python.org/pypi/vobject
"""

import vobject
from vobject.vcard import Name, Address

from bbdb.utils import anniversaries


def vcards(db):
    """
    Yield vcards from a BBDB database.
    """

    for rec in db.records:
        card = vobject.vCard()

        attr = card.add('fn')
        attr.value = rec.name

        attr = card.add('n')
        attr.value = Name(given=rec.firstname, family=rec.lastname)

        for tag, addr in rec.address.items():
            attr = card.add('adr')
            attr.type_param = tag
            attr.value = Address(street=addr.location, city=addr.city,
                                 region=addr.state, code=addr.zipcode,
                                 country=addr.country)

        for tag, number in rec.phone.items():
            attr = card.add('tel')
            attr.type_param = tag
            attr.value = number

        if rec.company:
            attr = card.add('org')
            attr.value = [rec.company]

        for addr in rec.net:
            attr = card.add('email')
            attr.value = addr

        for aka in rec.aka:
            attr = card.add('nickname')
            attr.value = aka

        for key, value in rec.fields.items():
            attr = card.add("X-BBDB-" + key)
            attr.value = value

        for tag, date in anniversaries(rec):
            if tag.startswith('birth'):
                tag = 'bday'
            else:
                tag = 'anniversary'

            year, month, day = date
            year = "%04d" % year if year else '----'

            attr = card.add(tag)
            attr.value = "%s%02d%02d" % (year, month, day)

        yield card


if __name__ == "__main__":
    from bbdb.database import readdb

    db = readdb()
    for card in vcards(db):
        print card.serialize()
