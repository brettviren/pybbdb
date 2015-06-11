"""
Interface to BBDB, the Insidious Big Brother Database.
"""

import re
import sys

from collections import OrderedDict
from functools import total_ordering

from pyparsing import (Regex, QuotedString, Keyword, Suppress, Word,
                       Group, OneOrMore, ZeroOrMore, Or, nums, alphanums)


def make_grammar():
    """
    Construct the BBDB grammar.  See bbdb.ebnf for the specification.
    """

    # Define the low-level entities.
    string = QuotedString(quoteChar='"', escChar='\\')
    string.setParseAction(lambda t: t[0])

    nil = Keyword("nil")
    nil.setParseAction(lambda t: [None])

    atom = Word(alphanums + '-')
    dot = Suppress(Keyword("."))

    integer = Word(nums)
    integer.setParseAction(lambda t: int(t[0]))

    # Helper functions for the brace types.
    LP, RP, LB, RB = map(Suppress, "()[]")
    Paren = lambda arg: LP + Group(arg) + RP
    Bracket = lambda arg: LB + Group(arg) + RB

    # Helper functions for building return values.
    def make_dict(t):
        d = Dict()
        if t[0]:
            for k, v in t[0]:
                d[k] = v
        return d

    def make_address_entry(t):
        return t[0].tag, Address(location=t[0].location or [],
                                 city=t[0].city or "",
                                 state=t[0].state or "",
                                 zipcode=t[0].zipcode or "",
                                 country=t[0].country or "")

    def make_record(t):
        return Record(firstname=t[0].firstname,
                      lastname=t[0].lastname,
                      aka=t[0].aka or [],
                      company=t[0].company or "",
                      phone=t[0].phone or {},
                      address=t[0].address or {},
                      net=t[0].net or [],
                      fields=t[0].fields or {})

    # Phone.
    phone_usa = Group(OneOrMore(integer))
    phone_nonusa = string
    phone_entry = Bracket(string("tag") + Or([phone_usa, phone_nonusa]))
    phone = Or([Paren(OneOrMore(phone_entry)), nil])("phone")
    phone.setParseAction(make_dict)

    # Address.
    location = Paren(OneOrMore(string))("location")
    location.setParseAction(lambda t: t.asList())

    address_entry = Bracket(string("tag") + location + string("city") +
                            string("state") + string("zipcode") +
                            string("country"))
    address_entry.setParseAction(make_address_entry)
    address = Or([Paren(OneOrMore(address_entry)), nil])("address")
    address.setParseAction(make_dict)

    # Field.
    field = Paren(atom + dot + string)
    fields = Or([Paren(OneOrMore(field)), nil])("fields")
    fields.setParseAction(make_dict)

    # Other parts of an entry.
    name = string("firstname") + string("lastname")
    company = Or([string, nil])("company")

    aka = Or([Paren(OneOrMore(string)), nil])("aka")
    aka.setParseAction(lambda t: t.asList())

    net = Or([Paren(OneOrMore(string)), nil])("net")
    net.setParseAction(lambda t: t.asList())

    cache = nil("cache")

    # A single record.
    record = Bracket(name + aka + company + phone + address + net +
                     fields + cache)

    record.setParseAction(make_record)

    # All the records.
    bbdb = ZeroOrMore(record)
    bbdb.setParseAction(lambda t: t.asList())

    # Define comment syntax.
    comment = Regex(r";.*")
    bbdb.ignore(comment)

    return bbdb


@total_ordering
class Dict(OrderedDict):
    """
    Base dictionary type.
    """

    def __init__(self, *args, **kw):
        super(Dict, self).__init__(*args, **kw)

    def __lt__(self, other):
        return list(self.items()) < list(other.items())

    def sort(self):
        items = sorted(self.items())
        self.clear()
        self.update(items)


class BBDB(Dict):
    """
    A BBDB database.
    """

    _props = (("coding", r"coding: (.+);", lambda s: s),
             ("fileversion", r"file-version: (\d+)", lambda s: int(s)))

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
        return BBDB(**d)

    def read_file(self, path):
        with open(path) as fp:
            self.read(fp)

    def read(self, fp=sys.stdin):
        text = fp.read()

        for line in text.split("\n"):
            if line.startswith(";"):
                for attr, regexp, func in self._props:
                    m = re.search(regexp, line)
                    if m:
                        self[attr] = func(m.group(1))

        records = parse(text)
        self.records.extend(records)

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


class Record(Dict):
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
        self["phone"] = Dict(phone)
        self["address"] = Dict()
        self["net"] = kw.get("net", [])
        self["fields"] = Dict(fields)

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
        self["fields"][tag] = text
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


class Address(Dict):
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


def parse(text):
    return grammar.parseString(text, parseAll=True)


def quote(string):
    return '"' + string.replace('"', r'\"') + '"'


grammar = make_grammar()
