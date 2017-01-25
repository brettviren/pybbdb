"""
The BBDB parser.
"""

import re

from pyparsing import (Regex, QuotedString, Keyword, Suppress, Word,
                       Group, OneOrMore, ZeroOrMore, Or, nums, alphanums)


# File properties appearing in header comments.
properties = (("coding", r"coding: (.+);", lambda s: s),
              ("fileversion", r"file-version: (\d+)", lambda s: int(s)))


def parse(text):
    data = {}

    # Extract properties from comment lines.
    for line in text.split("\n"):
        if line.startswith(";"):
            for attr, regexp, func in properties:
                m = re.search(regexp, line)
                if m:
                    data[attr] = func(m.group(1))

    # Parse text for BBDB records.
    results = grammar.parseString(text, parseAll=True)
    data["records"] = list(results)

    return data


def make_grammar():
    """
    Construct the BBDB grammar.  See grammar.ebnf for the specification.
    """

    # Helper functions for the brace types.
    LP, RP, LB, RB = map(Suppress, "()[]")
    Paren = lambda arg: LP + Group(arg) + RP
    Bracket = lambda arg: LB + Group(arg) + RB

    # Helper functions for constructing return types.
    def make_list(t):
        return t.asList()

    def make_dict(t):
        return {k: v for k, v in t[0] or []}

    def make_address_entry(t):
        return t[0].tag, {"location": list(t[0].location or []),
                          "city": t[0].city or "",
                          "state": t[0].state or "",
                          "zipcode": t[0].zipcode or "",
                          "country": t[0].country or ""}

    def make_record(t):
        return {"firstname": t[0].firstname,
                "lastname": t[0].lastname,
                "aka": t[0].aka or [],
                "company": t[0].company or "",
                "phone": t[0].phone or {},
                "address": t[0].address or {},
                "net": t[0].net or [],
                "fields": t[0].fields or {}}

    def make_string(t):
        return t[0][1:-1].replace(r'\"', '"')

    # Define the low-level entities.
    string = QuotedString(quoteChar='"', escChar='\\', unquoteResults=False)
    string.setParseAction(make_string)

    nil = Keyword("nil")
    nil.setParseAction(lambda t: [None])

    atom = Word(alphanums + '-')
    dot = Suppress(Keyword("."))

    integer = Word(nums)
    integer.setParseAction(lambda t: int(t[0]))

    # Phone.
    phone_usa = Group(OneOrMore(integer))
    phone_nonusa = string
    phone_entry = Bracket(string("tag") + Or([phone_usa, phone_nonusa]))
    phone = Or([Paren(OneOrMore(phone_entry)), nil])("phone")
    phone.setParseAction(make_dict)

    # Address.
    location = Paren(OneOrMore(string))("location")
    location.setParseAction(make_list)

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
    name = string("firstname") + Or([string("lastname"), nil])
    company = Or([string, nil])("company")

    aka = Or([Paren(OneOrMore(string)), nil])("aka")
    aka.setParseAction(make_list)

    net = Or([Paren(OneOrMore(string)), nil])("net")
    net.setParseAction(make_list)

    cache = nil("cache")

    # A single record.
    record = Bracket(name + aka + company + phone + address + net +
                     fields + cache)

    record.setParseAction(make_record)

    # All the records.
    bbdb = ZeroOrMore(record)
    bbdb.setParseAction(make_list)

    # Define comment syntax.
    comment = Regex(r";.*")
    bbdb.ignore(comment)

    return bbdb


# Build the BBDB grammar.
grammar = make_grammar()


if __name__ == "__main__":
    import sys
    import json

    text = open("parser.el").read()
    data = parse(text)
    json.dump(data, sys.stdout, indent=4)
