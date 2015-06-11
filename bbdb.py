"""
Interface to BBDB, the Insidious Big Brother Database.
"""

import re
import sys
from collections import OrderedDict as odict

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
    def make_odict(t):
        d = odict()
        if t[0]:
            for k, v in t[0]:
                d[k] = v
        return d

    def make_address_entry(t):
        return t[0].tag, Address(lines=t[0].lines,
                                 city=t[0].city,
                                 state=t[0].state,
                                 zipcode=t[0].zipcode,
                                 country=t[0].country)

    def make_record(t):
        return Record(firstname=t[0].firstname,
                      lastname=t[0].lastname,
                      aka=t[0].aka,
                      company=t[0].company,
                      phone=t[0].phone,
                      address=t[0].address,
                      net=t[0].net,
                      fields=t[0].fields,
                      cache=t[0].cache)

    # Phone.
    phone_usa = Group(OneOrMore(integer))
    phone_nonusa = string
    phone_entry = Bracket(string("tag") + Or([phone_usa, phone_nonusa]))
    phone = Or([Paren(OneOrMore(phone_entry)), nil])("phone")
    phone.setParseAction(make_odict)

    # Address.
    lines = Paren(OneOrMore(string))("lines")
    lines.setParseAction(lambda t: t.asList())

    address_entry = Bracket(string("tag") + lines + string("city") +
                            string("state") + string("zipcode") +
                            string("country"))
    address_entry.setParseAction(make_address_entry)
    address = Or([Paren(OneOrMore(address_entry)), nil])("address")
    address.setParseAction(make_odict)

    # Field.
    field = Paren(atom + dot + string)
    fields = Or([Paren(OneOrMore(field)), nil])("fields")
    fields.setParseAction(make_odict)

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


class BBDB(odict):
    """
    A BBDB database.
    """

    props = (("coding", r"coding: (.+);", lambda s: s),
             ("fileversion", r"file-version: (\d+)", lambda s: int(s)),
             ("userfields", r"user-fields: \((.+)\)", lambda s: s.split()))

    def __init__(self, path=None, **kw):
        super(BBDB, self).__init__()

        self["coding"] = kw.get("coding", "utf-8-emacs")
        self["fileversion"] = kw.get("fileversion", 6)
        self["userfields"] = kw.get("userfields", [])
        self["records"] = []

        for data in kw.get("records", []):
            self["records"].append(Record(**data))

        if path:
            self.read_file(path)

    @property
    def coding(self):
        return self["coding"]

    @property
    def fileversion(self):
        return self["fileversion"]

    @property
    def userfields(self):
        return self["userfields"]

    @property
    def records(self):
        return self["records"]

    def read(self, fp=sys.stdin):
        text = fp.read()

        for line in text.split("\n"):
            if line.startswith(";"):
                for attr, regexp, func in self.props:
                    m = re.search(regexp, line)
                    if m:
                        self[attr] = func(m.group(1))

        records = parse(text)
        self.records.extend(records)

    def read_file(self, path):
        with open(path) as fp:
            self.read(fp)

    def add_record(self, firstname="", lastname="", aka=[], company="",
                   phone={}, address={}, net=[], fields={}):
        rec = Record(firstname=firstname, lastname=lastname, aka=aka,
                     company=company, phone=phone, address=address,
                     net=net, fields=fields)
        self.records.append(rec)
        return rec

    def update_fields(self):
        for rec in self.records:
            for tag in rec.fields:
                if tag not in self.userfields:
                    self.userfields.append(tag)

    def write(self, fp=sys.stdout):
        self.update_fields()

        fp.write(";; -*-coding: %s;-*-\n" % self.coding)
        fp.write(";;; file-version: %d\n" % self.fileversion)
        fp.write(";;; user-fields: (%s)\n" % " ".join(self.userfields))

        for rec in self.records:
            fp.write("[")
            fp.write(" ".join(list(rec.outputs())))
            fp.write("]\n")

    def write_file(self, path):
        with open(path, "wb") as fp:
            self.write(fp)

    def __repr__(self):
        return "<BBDB: %d records>" % len(self.records)


class Record(odict):
    """
    A single BBDB record.
    """

    def __init__(self, **kw):
        super(Record, self).__init__()

        self["firstname"] = kw.get("firstname", "")
        self["lastname"] = kw.get("lastname", "")
        self["company"] = kw.get("company", "")
        self["aka"] = kw.get("aka", [])
        self["phone"] = odict(kw.get("phone", {}))
        self["address"] = odict()
        self["net"] = kw.get("net", [])
        self["fields"] = odict(kw.get("fields", {}))
        self["cache"] = kw.get("cache", None)

        for tag, data in kw.get("address", {}).items():
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

    def add_address(self, tag, lines=[], city="", state="",
                    zipcode="", country=""):
        address = Address(lines=lines, city=city, state=state,
                          zipcode=zipcode, country=country)
        self["address"][tag] = address
        return address

    def add_net(self, *names):
        self["net"].extend(names)

    def add_field(self, tag, text):
        self["fields"][tag] = text

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
            for items in self.phone.items():
                rec.append("[" + " ".join(map(quote, items)) + "]")
            yield "(" + " ".join(rec) + ")"
        else:
            yield "nil"

        if self.address:
            rec = []
            for tag, address in self.address.items():
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
            for tag, text in self.fields.items():
                rec.append("(" + tag + " . " + quote(text) + ")")
            yield "(" + " ".join(rec) + ")"
        else:
            yield "nil"

        yield "nil"

    def __repr__(self):
        return "<Record: %s>" % self.name


class Address(odict):
    def __init__(self, **kw):
        super(Address, self).__init__()

        self["lines"] = list(kw.get("lines", []))
        self["city"] = kw.get("city", "")
        self["state"] = kw.get("state", "")
        self["zipcode"] = kw.get("zipcode", "")
        self["country"] = kw.get("country", "")

    def add_line(self, *lines):
        self["lines"].extend(lines)

    def set_city(self, city):
        self["city"] = city

    def set_state(self, state):
        self["state"] = state

    def set_zipcode(self, zipcode):
        self["zipcode"] = zipcode

    def set_country(self, country):
        self["country"] = country

    @property
    def lines(self):
        return self["lines"]

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
        if self.lines:
            yield "(" + " ".join(map(quote, self.lines)) + ")"
        else:
            yield "nil"

        yield quote(self.city)
        yield quote(self.state)
        yield quote(self.zipcode)
        yield quote(self.country)

    def __str__(self):
        lines = self.lines[:]

        if self.city:
            lines.append(self.city)

        if self.state:
            lines.append(self.state)

        if self.zipcode:
            lines.append(self.zipcode)

        if self.country:
            lines.append(self.country)

        return ", ".join(lines)

    def __repr__(self):
        return "<Address: %s>" % str(self)


def parse(text):
    return grammar.parseString(text, parseAll=True)


def quote(string):
    return '"' + string.replace('"', r'\"') + '"'


grammar = make_grammar()
