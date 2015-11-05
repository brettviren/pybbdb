"""
Data validation schema.
"""

from voluptuous import Schema, Required, MultipleInvalid
from six import text_type as text


def validate(data):
    "Check data is a valid BBDB database."

    try:
        return database(data)
    except MultipleInvalid as e:
        path = '.'.join(map(str, e.path))
        raise ValueError("%s: %s" % (path, e.msg))


address = Schema({Required('location'): [text],
                  Required('city', default=""): text,
                  Required('state', default=""): text,
                  Required('zipcode', default=""): text,
                  Required('country', default=""): text})


record = Schema({Required('firstname'): text,
                 Required('lastname'): text,
                 'company': text,
                 'aka': [text],
                 'phone': {text: text},
                 'address': {text: address},
                 'net': [text],
                 'fields': {text: text}})


database = Schema({'coding': text,
                   'fileversion': int,
                   'records': [record]})


if __name__ == "__main__":
    import json
    with open("schema.json") as fp:
        data = json.load(fp)

    validate(data)
