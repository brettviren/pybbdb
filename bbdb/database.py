"""
The BBDB database.
"""

import sys

from . import parser
from .schema import validate
from .utils import SortedDict, bbdb_file, quote


class BBDB(SortedDict):
    """
    A BBDB database.
    """

    def __init__(self, **kw):
        super(BBDB, self).__init__()

        recdata = kw.get("records", [])
        records = [Record(**rec) for rec in recdata]
        records.sort()

        self["coding"] = kw.get("coding", "utf-8-emacs")
        self["fileversion"] = kw.get("fileversion", 6)
        self["records"] = records

    def add_record(self, firstname, lastname, aka=None, company="",
                   phone=None, address=None, net=None, fields=None):
        rec = Record(firstname=firstname, lastname=lastname,
                     aka=aka or [], company=company, phone=phone or {},
                     address=address or {}, net=net or [],
                     fields=fields or {})

        self.records.append(rec)
        self.records.sort()

        return rec

    @staticmethod
    def fromfile(path):
        db = BBDB()
        db.read_file(path)
        return db

    @staticmethod
    def fromdict(d):
        d = validate(d)
        return BBDB(**d)

    def read_file(self, path):
        with open(path) as fp:
            self.read(fp)

    def read(self, fp=sys.stdin):
        text = fp.read()
        data = parser.parse(text)

        for attr, value in data.items():
            if attr == "records":
                records = [Record(**rec) for rec in value]
                self.records.extend(records)
            else:
                self[attr] = value

    def write_file(self, path):
        with open(path, "w") as fp:
            self.write(fp)

    def write(self, fp=sys.stdout):
        fields = set()
        for rec in self.records:
            for tag in rec.fields:
                fields.add(tag)

        fp.write(";; -*-coding: %s;-*-\n" % self.coding)
        fp.write(";;; file-version: %d\n" % self.fileversion)
        fp.write(";;; user-fields: (%s)\n" % " ".join(self.userfields))

        for rec in sorted(self.records):
            fp.write("[")
            fp.write(" ".join(list(rec.outputs())))
            fp.write("]\n")

    @property
    def coding(self):
        return self["coding"]

    @property
    def fileversion(self):
        return self["fileversion"]

    @property
    def userfields(self):
        fields = set()
        for rec in self.records:
            for tag in rec.fields:
                fields.add(tag)

        return list(sorted(fields))

    @property
    def records(self):
        return self["records"]

    def __repr__(self):
        return "<BBDB: %d records>" % len(self.records)


class Record(SortedDict):
    """
    A single BBDB record.
    """

    def __init__(self, **kw):
        super(Record, self).__init__()

        phone = sorted(kw.get("phone", {}).items())
        fields = sorted(kw.get("fields", {}).items())
        address = sorted(kw.get("address", {}).items())

        self["firstname"] = kw.get("firstname", "")
        self["lastname"] = kw.get("lastname", "")
        self["company"] = kw.get("company", "")
        self["aka"] = kw.get("aka", [])
        self["phone"] = SortedDict(phone)
        self["address"] = SortedDict()
        self["net"] = kw.get("net", [])
        self["fields"] = SortedDict(fields)

        for tag, data in address:
            self["address"][tag] = Address(**data)

    def set_name(self, firstname, lastname):
        self.set_firstname(firstname)
        self.set_lastname(lastname)

    def set_firstname(self, firstname):
        self["firstname"] = firstname

    def set_lastname(self, lastname):
        self["lastname"] = lastname

    def add_aka(self, *names):
        self["aka"].extend(names)

    def set_company(self, company):
        self["company"] = company

    def add_phone(self, tag, number):
        self["phone"][tag] = number
        self["phone"].sort()

    def add_address(self, tag, location=None, city="", state="",
                    zipcode="", country=""):
        address = Address(location=location or [], city=city, state=state,
                          zipcode=zipcode, country=country)

        self["address"][tag] = address
        self["address"].sort()

        return address

    def add_net(self, *names):
        self["net"].extend(names)

    def add_field(self, tag, text):
        self["fields"][tag] = text.replace("\n", r'\n')
        self["fields"].sort()

    @property
    def name(self):
        return self.firstname + " " + self.lastname

    @property
    def firstname(self):
        return self["firstname"]

    @property
    def lastname(self):
        return self["lastname"]

    @property
    def aka(self):
        return self["aka"]

    @property
    def company(self):
        return self["company"]

    @property
    def phone(self):
        return self["phone"]

    @property
    def address(self):
        return self["address"]

    @property
    def net(self):
        return self["net"]

    @property
    def fields(self):
        return self["fields"]

    def outputs(self):
        yield quote(self.firstname)
        yield quote(self.lastname)

        if self.aka:
            yield "(" + " ".join(map(quote, self.aka)) + ")"
        else:
            yield "nil"

        if self.company:
            yield quote(self.company)
        else:
            yield "nil"

        if self.phone:
            rec = []
            for items in sorted(self.phone.items()):
                rec.append("[" + " ".join(map(quote, items)) + "]")
            yield "(" + " ".join(rec) + ")"
        else:
            yield "nil"

        if self.address:
            rec = []
            for tag, address in sorted(self.address.items()):
                addr = " ".join(list(address.outputs()))
                rec.append("[" + quote(tag) + " " + addr + "]")
            yield "(" + " ".join(rec) + ")"
        else:
            yield "nil"

        if self.net:
            yield "(" + " ".join(map(quote, self.net)) + ")"
        else:
            yield "nil"

        if self.fields:
            rec = []
            for tag, text in sorted(self.fields.items()):
                rec.append("(" + tag + " . " + quote(text) + ")")
            yield "(" + " ".join(rec) + ")"
        else:
            yield "nil"

        yield "nil"

    def __repr__(self):
        return "<Record: %s>" % self.name


class Address(SortedDict):
    def __init__(self, **kw):
        super(Address, self).__init__()

        self["location"] = list(kw.get("location", []))
        self["city"] = kw.get("city", "")
        self["state"] = kw.get("state", "")
        self["zipcode"] = kw.get("zipcode", "")
        self["country"] = kw.get("country", "")

    def add_location(self, *location):
        self["location"].extend(location)

    def set_city(self, city):
        self["city"] = city

    def set_state(self, state):
        self["state"] = state

    def set_zipcode(self, zipcode):
        self["zipcode"] = zipcode

    def set_country(self, country):
        self["country"] = country

    @property
    def description(self):
        parts = self.location[:]

        for attr in "city", "state", "zipcode", "country":
            if self[attr]:
                parts.append(self[attr])

        return ", ".join(parts)

    @property
    def location(self):
        return self["location"]

    @property
    def city(self):
        return self["city"]

    @property
    def state(self):
        return self["state"]

    @property
    def zipcode(self):
        return self["zipcode"]

    @property
    def country(self):
        return self["country"]

    def outputs(self):
        if self.location:
            yield "(" + " ".join(map(quote, self.location)) + ")"
        else:
            yield "nil"

        yield quote(self.city)
        yield quote(self.state)
        yield quote(self.zipcode)
        yield quote(self.country)

    def __repr__(self):
        return "<Address: %s>" % self.description


def readdb(path=None, default="bbdb.el"):
    "Read a BBDB database."

    if not path:
        if len(sys.argv) > 1:
            path = sys.argv[1]
        else:
            path = bbdb_file() or default

    return BBDB.fromfile(path)
