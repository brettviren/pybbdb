"""
Interface to BBDB, the Insidious Big Brother Database.
"""

import re
import sys
from collections import OrderedDict

from pyparsing import (Regex, QuotedString, Keyword, Suppress, Word,
                       Group, OneOrMore, ZeroOrMore, Or, nums, alphanums)

_props = (("coding", r"coding: (.+);", lambda text: text),
          ("fileversion", r"file-version: (\d+)", lambda text: int(text)),
          ("userfields", r"user-fields: \((.+)\)", lambda text: text.split()))


class BBDB(list):
    """
    A BBDB database.
    """

    def __init__(self, path=None, coding="utf-8-emacs", userfields=[]):
        self.coding = coding
        self.fileversion = 6
        self.userfields = userfields

        if path:
            self.read_file(path)

    def read(self, fp=sys.stdin):
        for line in fp:
            if line.startswith(";"):
                for attr, regexp, func in _props:
                    m = re.search(regexp, line)
                    if m:
                        setattr(self, attr, func(m.group(1)))
            else:
                data = grammar.parseString(line, parseAll=True)
                self.add(*data[0])

    def read_file(self, path):
        with open(path) as fp:
            self.read(fp)

    def add(self, *args, **kw):
        entry = BBDBEntry(*args, **kw)
        self.append(entry)
        return entry

    def update_fields(self):
        for entry in self:
            for tag in entry.fields:
                if tag not in self.userfields:
                    self.userfields.append(tag)

    def write(self, fp=sys.stdout):
        self.update_fields()

        fp.write(";; -*-coding: %s;-*-\n" % self.coding)
        fp.write(";;; file-version: %d\n" % self.fileversion)
        fp.write(";;; user-fields: (%s)\n" % " ".join(self.userfields))

        for entry in self:
            fp.write("[")
            fp.write(" ".join(list(entry.records())))
            fp.write("]\n")

    def write_file(self, path):
        with open(path, "wb") as fp:
            self.write(fp)

    def __repr__(self):
        return "<BBDB: %d entries>" % len(self)


class BBDBItem(OrderedDict):
    def __init__(self):
        super(BBDBItem, self).__init__()


class BBDBEntry(BBDBItem):
    """
    A single BBDB entry.
    """

    def __init__(self, firstname="", lastname="", aka=[], company="",
                 phone=[], address=[], net=[], fields=[], cache=None):
        super(BBDBEntry, self).__init__()

        self.set_name(firstname, lastname)
        self.set_company(company)

        self["aka"] = []
        if aka:
            for name in aka:
                self.add_aka(name)

        self["phone"] = BBDBItem()
        if phone:
            for tag, number in phone:
                self.add_phone(tag, number)

        self["address"] = BBDBItem()
        if address:
            for args in address:
                self.add_address(*args)

        self["net"] = []
        if net:
            for name in net:
                self.add_net(name)

        self["fields"] = BBDBItem()
        if fields:
            for tag, text in fields:
                self.add_field(tag, text)

        self["cache"] = cache

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
        address = BBDBAddress(lines, city, state, zipcode, country)
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

    def records(self):
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
                addr = " ".join(list(address.records()))
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
        return "<BBDBEntry: %s>" % self.name


class BBDBAddress(BBDBItem):
    def __init__(self, lines=[], city="", state="", zipcode="", country=""):
        super(BBDBAddress, self).__init__()

        self["lines"] = list(lines)

        self.set_city(city)
        self.set_state(state)
        self.set_zipcode(zipcode)
        self.set_country(country)

    def set_city(self, city):
        self["city"] = city

    def set_state(self, state):
        self["state"] = state

    def set_zipcode(self, zipcode):
        self["zipcode"] = zipcode

    def set_country(self, country):
        self["country"] = country

    def add_line(self, *lines):
        self["lines"].extend(lines)

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

    def records(self):
        if self.lines:
            yield "(" + " ".join(map(quote, self.lines)) + ")"
        else:
            yield "nil"

        yield quote(self.city)
        yield quote(self.state)
        yield quote(self.zipcode)
        yield quote(self.country)

    def __repr__(self):
        return "<BBDBAddress: %s>" % " ".join(list(self.records()))


def make_grammar():
    """
    Construct the BBDB grammar.  See bbdb.ebnf for the specification.
    """

    # Define the low-level entities.
    string = QuotedString(quoteChar='"', escChar='\\')
    string.setParseAction(lambda tokens: tokens[0])

    nil = Keyword("nil")
    nil.setParseAction(lambda tokens: [None])

    atom = Word(alphanums + '-')
    dot = Suppress(Keyword("."))

    integer = Word(nums)
    integer.setParseAction(lambda tokens: int(tokens[0]))

    # Define helper functions for the brace types.
    LP, RP, LB, RB = map(Suppress, "()[]")
    Paren = lambda arg: LP + Group(arg) + RP
    Bracket = lambda arg: LB + Group(arg) + RB

    # Phone.
    phone_usa = Group(OneOrMore(integer))
    phone_nonusa = string
    phone = Bracket(string + Or([phone_usa, phone_nonusa]))

    # Address.
    address_lines = Paren(OneOrMore(string))
    address = Bracket(string + address_lines + string * 4)

    # Field.
    field = Paren(atom + dot + string)

    # A single entry.
    bbdb_entry = Bracket(string("firstname") + string("lastname") +
                         Or([Paren(OneOrMore(string)), nil])("aka") +
                         Or([string, nil])("company") +
                         Or([Paren(OneOrMore(phone)), nil])("phone") +
                         Or([Paren(OneOrMore(address)), nil])("address") +
                         Or([Paren(OneOrMore(string)), nil])("net") +
                         Or([Paren(OneOrMore(field)), nil])("fields") +
                         nil("cache"))

    # All the entries.
    bbdb = ZeroOrMore(bbdb_entry)

    # Define comment syntax.
    comment = Regex(r";.*")
    bbdb.ignore(comment)

    return bbdb


def quote(string):
    return '"' + string.replace('"', r'\"') + '"'


grammar = make_grammar()
