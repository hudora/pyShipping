#!/usr/bin/env python
# encoding: utf-8
"""
fakt.py

Created by Christian Klein on 2011-03-31.
Copyright (c) 2011 HUDORA GmbH. All rights reserved.
"""

import csv
import StringIO


FIELDNAME_MAPPING = {
    'Firma': 'firma',
    'T-Datum': 'datum',
    'Frachtbrief': 'frachtbrief',
    'Versender-Ref.': 'lieferung_id',
    'Abs.-Name': 'absender_name1',
    'Abs.-Str.': 'absender_strasse',
    'Abs.-Land': 'absender_land',
    'Abs.-Plz': 'absender_plz',
    'Abs.-Ort': 'absender_ort',
    'Emp.-Name': 'empfaenger_name1',
    'Emp.-Str.': 'empfaenger_strasse',
    'Emp.-Land': 'empfaenger_land',
    'Emp.-Plz': 'empfaenger_plz',
    'Emp.-Ort': 'empfaenger_ort',
    'Zeichen+Nr.': 'zeichennr',
    'Inhalt': 'inhalt',
    'T-Gewicht': 'transportgewicht',
    'F-Gewicht': 'frachtpflgewicht',
    'KM': 'kilometer',
    'VPE': 'einheiten',
    'EURO': 'euro',
    'GIBO': 'gibo',
    'Fracht': 'fracht',
    'Maut': 'maut',
    'Summe': 'summe'}


def parse_fakt(data):
    """Parse BORDERO FAKT data"""

    if isinstance(data, basestring):
        data = StringIO.StringIO(data)

    header = data.readline()
    if not header.strip() == '@@PHFAKT128 FROMAT:CSV DELIMITER:;':
        raise ValueError('Unknown header: %r' % header)

    reader = csv.DictReader(data, delimiter=';')
    fieldnames = reader.fieldnames
    for index, field in enumerate(fieldnames):
        if field in MAPPING:
            del fieldnames[index]
            fieldnames.insert(index, FIELDNAME_MAPPING[field])
    reader.fieldnames = fieldnames

    rows = [row for row in reader]
    return rows


if __name__ == "__main__":
    import sys
    import pprint
    pprint.pprint(parse_fakt(open(sys.argv[1]).read()))
