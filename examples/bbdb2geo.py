"""
Convert BBDB entries to GeoJSON format.

This looks up the locations of addresses, and adds a GeoJSON entry for each
one that's found.

Requires:
   geopy -- https://pypi.python.org/pypi/geopy
   geojson -- https://pypi.python.org/pypi/geojson
"""

import sys
import geojson

from geojson import GeoJSON, FeatureCollection, Feature, Point
from geopy.geocoders import Nominatim

from collections import OrderedDict

_ignoredprops = ["creation-date", "timestamp"]


def bbdb2geo(db, geocoder=None):
    return GeoJSON(FeatureCollection(list(features(db, geocoder))))


def features(db, geocoder):
    if not geocoder:
        geocoder = Nominatim(timeout=10)

    for rec in db.records:
        for tag, addr in rec.address.items():
            place = addr.description
            loc = geocoder.geocode(place)

            if not loc and addr.zipcode:
                loc = geocoder.geocode(addr.zipcode)

            if loc:
                yield rec2feature(rec, addr, loc.latitude, loc.longitude)
            else:
                sys.stderr.write("Can't locate: %s\n" % place)


def rec2feature(rec, address, lat, lon):
    props = OrderedDict()

    props["name"] = rec.name
    props["Address"] = address.description

    if rec.aka:
        props["AKA"] = ", ".join(rec.aka)

    if rec.company:
        props["Company"] = rec.company

    if rec.phone:
        for tag, number in rec.phone.items():
            props["Phone (%s)" % tag] = number

    if rec.net:
        props["Email"] = "\n".join(rec.net)

    for key, value in rec.fields.items():
        if key not in _ignoredprops:
            props[key.capitalize()] = value

    return Feature(geometry=Point((lon, lat)), properties=props)


if __name__ == "__main__":
    from bbdb.database import readdb

    db = readdb()
    geo = bbdb2geo(db)
    geojson.dump(geo, sys.stdout, indent=4)
