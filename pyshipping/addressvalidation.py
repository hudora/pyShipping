#!/usr/bin/env python
# encoding: utf-8
"""
addressvalidation.py - check the validity of addresses

Should once integrate with
http://www.deutschepost.de/dpag?tab=1&skin=hi&check=yes&lang=de_DE&xmlFile=link1015574_1021
http://www.isogmbh.de/leistungen/dataquality-management/adressvalidierung.html
or http://opengeodb.hoppe-media.com/


Created by Maximillian Dornseif on 2009-09-03.
Copyright (c) 2009, 2010 HUDORA. All rights reserved.
"""

import unittest


def validate(adr, servicelevel=1):
    """Validates an address and returns a possibly corrected address.

    'adr' should be a object conforming to the address protocol
        - see http://cybernetics.hudora.biz/projects/wiki/AddressProtocol
    'servicelevel' can be an integer with the following values:
    1 - generic validation, no money/effort should be spend on correction and suggestions
    2 - TBD.

    returns (status, message, [corrected addresses and variants])

    status can be:
    '10invalid' - address is for sure non deliverable in this form
    '20troubled' - bounced before or is unlikely to be correct - possible alternatives are returned
    '30ok' - likely to work
    '31ok' - likely to work but was corrected
    '40verified' - we are sure it works
    """

    adr['land'] = adr['land'].strip()
    adr['plz'] = adr['plz'].strip()

    if adr['land'] != 'IE' and not adr['plz']:
        return ('10invalid', 'Postleitzahl fehlt', [adr])

    if adr['land'] == 'DE' and len(adr.get('plz', '')) != 5:
        return ('10invalid', 'Postleitzahl fehlerhaft', [adr])

    return ('30ok', '', [adr])


class AddressvalidationTests(unittest.TestCase):
    """Tests for the address validation facility."""

    def setUp(self):
        """Set up test address base."""
        self.address = {'name1': 'HUDORA GmbH',
                        'name2': 'Abt. Cybernetics',
                        'strasse': 'Jägerwald 13',
                        'land': 'DE',
                        'plz': '42897',
                        'ort': 'Remscheid',
                        'tel': '+49 2191 60912 0',
                        'fax': '+49 2191 60912 50',
                        'mobil': '+49 175 00000xx',
                        'email': 'nobody@hudora.de'}

    def test_good_address(self):
        """Test if correct addresses are considered correct."""
        self.assertEqual(validate(self.address)[0], '30ok')
        self.assertEqual(validate(self.address)[1], '')

    def test_missing_zip(self):
        """Test if correct addresses are considered correct."""
        self.address['plz'] = ''
        self.assertEqual(validate(self.address)[0], '10invalid')

    def test_short_zip(self):
        """Test if correct addresses are considered correct."""
        self.address['plz'] = '123'
        self.assertEqual(validate(self.address)[0], '10invalid')

    def test_long_zip(self):
        """Test if correct addresses are considered correct."""
        self.address['plz'] = '12345 Rade'
        self.assertEqual(validate(self.address)[0], '10invalid')


if __name__ == '__main__':
    unittest.main()
