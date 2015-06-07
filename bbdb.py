"""
Interface to the Insidious Big Brother Database

http://bbdb.sourceforge.net

TODO: write output stuff
TODO: check file version
"""


import re
import sys

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

    def read_file(self, path):
        with open(path) as fp:
            for line in fp:
                if line.startswith(";"):
                    for attr, regexp, func in _props:
                        m = re.search(regexp, line)
                        if m:
                            setattr(self, attr, func(m.group(1)))
                else:
                    data = grammar.parseString(line, parseAll=True)
                    self.add(*data[0])

    def add(self, *args, **kw):
        entry = Entry(*args, **kw)
        self.append(entry)
        return entry

    def write(self, fp=sys.stdout):
        fp.write(";; -*-coding: %s;-*-\n" % self.coding)
        fp.write(";; file-version: %d\n" % self.fileversion)
        fp.write(";; user-fields: (%s)\n" % " ".join(self.userfields))

        for entry in self:
            entry.write(fp)

    def write_file(self, path):
        with open(path, "w") as fp:
            self.write(fp)


class BBDBItem(dict):
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        if attr in self:
            self[attr] = value
        else:
            raise AttributeError("entry has no attribute '%s'" % attr)


class Entry(BBDBItem):
    """
    A single BBDB entry.
    """

    def __init__(self, firstname="", lastname="", aka=[], company="",
                 phone=[], address=[], net=[], notes=[], cache=None):
        self["firstname"] = firstname
        self["lastname"] = lastname
        self["company"] = company

        self["aka"] = []
        if aka:
            for name in aka:
                self.add_aka(name)

        self["phone"] = {}
        if phone:
            for tag, number in phone:
                self.add_phone(tag, number)

        self["address"] = {}
        if address:
            for args in address:
                self.add_address(*args)

        self["net"] = []
        if net:
            for name in net:
                self.add_net(name)

        self["notes"] = {}
        if notes:
            for tag, text in notes:
                self.add_note(tag, text)

        self["cache"] = cache

    def set_name(self, firstname, lastname):
        self["firstname"] = firstname
        self["lastname"] = lastname

    def add_aka(self, name):
        self["aka"].append(name)

    def add_phone(self, tag, number):
        self["phone"][tag] = number

    def add_address(self, tag, streets=[], city="", state="",
                    zipcode="", country=""):
        address = Address(streets, city, state, zipcode, country)
        self["address"][tag] = address
        return address

    def add_net(self, name):
        self["net"].append(name)

    def add_note(self, tag, text):
        self["notes"][tag] = text

    @property
    def name(self):
        return (self.firstname + " " + self.lastname).strip()

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
                rec.append("[" + quote(tag) + " " + repr(address) + "]")
            yield "(" + " ".join(rec) + ")"
        else:
            yield "nil"

        # FINISH ME.

    def write(self, fp=sys.stdout):
        fp.write("[")
        fp.write(" ".join(list(self.records())))
        fp.write("]\n")


class Address(BBDBItem):
    def __init__(self, streets=[], city="", state="", zipcode="", country=""):
        self["streets"] = list(streets)
        self["city"] = city
        self["state"] = state
        self["zipcode"] = zipcode
        self["country"] = country

    def add_street(self, street):
        self["streets"].append(street)

    def records(self):
        if self.streets:
            yield "(" + " ".join(map(quote, self.streets)) + ")"
        else:
            yield "nil"

        yield quote(self.city)
        yield quote(self.state)
        yield quote(self.zipcode)
        yield quote(self.country)

    def __repr__(self):
        return "[" + " ".join(list(self.records())) + "]"


def make_grammar():
    """
    Construct the BBDB grammar.  See bbdb.ebnf for the specification.
    """

    # Define the low-level entities.
    string = QuotedString(quoteChar='"', escChar='\\')
    string.setParseAction(lambda tokens: tokens[0].strip())

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
    address_list = Paren(OneOrMore(string))
    address = Bracket(string + address_list + string * 4)

    # Note.
    note = Paren(atom + dot + string)

    # A single entry.
    bbdb_entry = Bracket(string("firstname") + string("lastname") +
                         Or([Paren(OneOrMore(string)), nil])("aka") +
                         Or([string, nil])("company") +
                         Or([Paren(OneOrMore(phone)), nil])("phone") +
                         Or([Paren(OneOrMore(address)), nil])("address") +
                         Or([Paren(OneOrMore(string)), nil])("net") +
                         Or([Paren(OneOrMore(note)), nil])("notes") +
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


if __name__ == "__main__":
    db = BBDB(userfields=['spouse', 'kids', 'catchphrase'])
    fred = db.add("Fred", "Flintstone")

    fred.add_phone("Home", "555-1234")

    fred.add_net("fred@bedrock.org")
    fred.add_note("spouse", "Wilma")
    fred.add_note("kids", "Pebbles, Bam-Bam")
    fred.add_note("catchphrase", '"Yabba dabba doo!"')

    fred.company = "Slate Rock & Gravel"

    home = fred.add_address("Home")
    home.add_street("345 Cavestone Road")
    home.city = "Bedrock"

    fred.add_aka("\"Freddie\"")
    fred.write()
