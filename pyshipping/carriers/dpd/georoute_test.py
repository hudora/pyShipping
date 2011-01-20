#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Test routing resolver for DPD. Coded by jmv, extended by md"""

import time
import unittest
from pyshipping.carriers.dpd.georoute import get_route, get_route_without_cache
from pyshipping.carriers.dpd.georoute import RouteData, Router, Destination
from pyshipping.carriers.dpd.georoute import ServiceError, CountryError, TranslationError


class TestCase(unittest.TestCase):
    """Provide sophisticated dictionary comparision."""

    def assertDicEq(self, dict1, dict2):
        """Asserts if two dicts are unequal.

        Raise an Exception which mentions the different entries of those dicts.
        """
        if dict1 != dict2:
            difference = set()
            for key, value in dict1.items():
                if dict2.get(key) != value:
                    difference.add((key, value, dict2.get(key)))
            for key, value in dict2.items():
                if dict1.get(key) != value:
                    difference.add((key, dict1.get(key), value))
            raise self.failureException, \
                ('%r != %r: %s' % (dict1, dict2, list(difference)))


class RouteDataTest(TestCase):

    def setUp(self):
        self.data = RouteData()
        self.db = self.data.db

    def test_version(self):
        self.assertEqual(self.data.version, '20100503')

    def test_get_country(self):
        self.assertRaises(CountryError, self.data.get_countrynum, 'URW')
        self.assertEqual(self.data.get_countrynum('JP'), '392')
        self.assertEqual(self.data.get_countrynum('DE'), '276')
        self.assertEqual(self.data.get_countrynum('de'), '276')

    def test_read_depots(self):
        c = self.db.cursor()
        c.execute("""SELECT * FROM depots WHERE DepotNumber=?""", ('0015', ))
        rows = c.fetchall()
        self.assertEqual(1, len(rows))
        self.assertEqual(('0015', '', '', 'Betriebsgesellschaft DPD Deutscher',
                          '', 'Otto-Hahn-Strasse 5', '', '59423', 'Unna', 'DE',
                          '+49-(0) 23 03-8 88-0', '+49-(0) 23 03-8 88-31', '', ''),
                         rows[0])

    def test_expand_depots(self):
        c = self.db.cursor()
        c.execute("""SELECT id
                     FROM routes
                     WHERE DestinationCountry='DE' AND BeginPostCode='42477'""")
        rows = c.fetchall()
        # Interestingly we sometimes get two routes
        # self.assertEqual(1, len(rows))
        route = rows[0][0]
        c.execute("SELECT depot FROM routedepots WHERE route=?", (route, ))
        rows = c.fetchall()
        self.assertEqual(1, len(rows))

    def test_get_service(self):
        self.assertEqual(self.data.get_service('180'), ('180', 'AM1-NO', '', '022,160', ''))
        self.assertRaises(ServiceError, self.data.get_service, '100000')

    def test_get_servicetext(self):
        text = self.data.get_servicetext('185')
        self.assertEqual('DPD 10:00 Unfrei / ex works', text)

    def test_translate_location(self):
        self.assertEqual('1', self.data.translate_location('Dublin', 'IE'))
        self.assertRaises(TranslationError, self.data.translate_location, 'Cahir', 'IE')


class RouterTest(TestCase):

    def setUp(self):
        self.data = RouteData()
        self.router = Router(self.data)

    def test_known_routes_de(self):
        route = self.router.route(Destination(postcode='42477'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0142', 'serviceinfo': '', 'country': u'DE',
                                               'd_sort': u'65', 'o_sort': u'42', 'service_text': u'D'})
        route = self.router.route(Destination(postcode='42897'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0142', 'serviceinfo': '', 'country': 'DE',
                                               'd_sort': '15', 'o_sort': '42', 'service_text': 'D'})
        route = self.router.route(Destination(postcode='53111'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0150', 'serviceinfo': '', 'country': 'DE',
                                               'd_sort': u'205', 'o_sort': '50', 'service_text': 'D'})
        route = self.router.route(Destination(postcode='53111', country='DE'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0150', 'serviceinfo': '', 'country': 'DE',
                                               'd_sort': u'205', 'o_sort': '50', 'service_text': 'D'})
        route = self.router.route(Destination('DE', '53111'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0150', 'serviceinfo': '', 'country': 'DE',
                                               'd_sort': u'205', 'o_sort': '50', 'service_text': 'D'})
        route = self.router.route(Destination('DE', '53111', city='Bonn'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0150', 'serviceinfo': '', 'country': 'DE',
                                               'd_sort': u'205', 'o_sort': '50', 'service_text': 'D'})
        route = self.router.route(Destination('DE', '53111', 'Bonn'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0150', 'serviceinfo': '', 'country': 'DE',
                                               'd_sort': u'205', 'o_sort': '50', 'service_text': 'D'})

    def test_known_routes_world(self):
        route = self.router.route(Destination(postcode='66400', country='FR'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0470', 'serviceinfo': '', 'country': u'FR',
                                               'd_sort': u'U53', 'o_sort': u'16', 'service_text': u'D'})
        route = self.router.route(Destination('FR', '66400', 'Ceret'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0470', 'serviceinfo': '', 'country': 'FR',
                                               'd_sort': 'U53', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination('BE', '3960', 'Bree/Belgien'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0532', 'serviceinfo': '', 'country': 'BE',
                                               'd_sort': u'A353', 'o_sort': '52', 'service_text': 'D'})
        route = self.router.route(Destination('CH', '6005', 'Luzern'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0616', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': '40', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('AT', '1210', 'Wien'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0622', 'serviceinfo': '', 'country': 'AT',
                                               'd_sort': '10', 'o_sort': '62', 'service_text': 'D'})
        route = self.router.route(Destination('AT', '4820', 'Bad Ischl'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0624', 'serviceinfo': '', 'country': 'AT',
                                               'd_sort': '63', 'o_sort': '62', 'service_text': 'D'})
        route = self.router.route(Destination('AT', '7400', 'Oberwart'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0628', 'serviceinfo': '', 'country': 'AT',
                                               'd_sort': u'3270', 'o_sort': '62', 'service_text': 'D'})
        route = self.router.route(Destination('AT', '4400', 'Steyr'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0624', 'serviceinfo': '', 'country': 'AT',
                                               'd_sort': '70', 'o_sort': '62', 'service_text': 'D'})
        route = self.router.route(Destination('AT', '1220', 'Wien'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0622', 'serviceinfo': '', 'country': 'AT',
                                               'd_sort': '30', 'o_sort': '62', 'service_text': 'D'})
        route = self.router.route(Destination('AT', '6890', 'Lustenau'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0627', 'serviceinfo': '', 'country': 'AT',
                                               'd_sort': '01', 'o_sort': '62', 'service_text': 'D'})
        route = self.router.route(Destination('BE', '3520', 'ZONHOVEN'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0532', 'serviceinfo': '', 'country': u'BE',
                                               'd_sort': u'A369', 'o_sort': u'52', 'service_text': u'D'})
        route = self.router.route(Destination('BE', '4890', 'Thimister'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0532', 'serviceinfo': '', 'country': 'BE',
                                               'd_sort': u'B326', 'o_sort': '52', 'service_text': 'D'})
        route = self.router.route(Destination('CH', '8305', 'Dietlikon'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0615', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': '77', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('CH', '4051', 'Basel'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0610', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': u'16', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('CH', '8808', 'Pf<C3><A4>ffikon'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0615', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': '71', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('DK', '9500', 'Hobro'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0504', 'serviceinfo': '', 'country': 'DK',
                                               'd_sort': u'405', 'o_sort': '20', 'service_text': 'D'})
        # Lichtenstein is routed via CH
        route = self.router.route(Destination('LI', '8399', 'Windhof / Luxembourg'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0617', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': '', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('LI', '9495', 'Triesen'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0617', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': '', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('LI', '8440', 'Steinfort'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0617', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': '', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('CZ', '41742', 'Krupka 1'))
        self.assertDicEq(route.routingdata(), {'d_depot': '1380', 'serviceinfo': '', 'country': 'CZ',
                                               'd_sort': '21', 'o_sort': '10', 'service_text': 'D'})
        route = self.router.route(Destination('ES', '28802', 'Alcala de Henares (Madrid)'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0728', 'serviceinfo': '', 'country': 'ES',
                                               'd_sort': '01', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination('ES', '28010', 'Madrid'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0728', 'serviceinfo': '', 'country': 'ES',
                                               'd_sort': '01', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination('FR', '84170', 'MONTEUX'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0447', 'serviceinfo': '', 'country': 'FR',
                                               'd_sort': u'S65', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination('FR', '91044', 'Evry Cedex'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0408', 'serviceinfo': '', 'country': u'FR',
                                               'd_sort': u'S61', 'o_sort': u'50', 'service_text': u'D'})

    def test_difficult_routingdepots(self):
        route = self.router.route(Destination('AT', '3626', 'H<C3><BC>nibach'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0623', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'01', 'o_sort': u'62', 'service_text': u'D'})
        route = self.router.route(Destination('AT', '8225', 'P<C3><B6>llau'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0628', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'1290', 'o_sort': u'62', 'service_text': u'D'})
        route = self.router.route(Destination('AT', '5020', 'Salzburg'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0625', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'1000', 'o_sort': u'62', 'service_text': u'D'})
        route = self.router.route(Destination('SE', '65224', 'Karlstad'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0307', 'serviceinfo': u'', 'country': 'SE',
                                               'd_sort': u'01', 'o_sort': u'20', 'service_text': u'D'})
        route = self.router.route(Destination('AT', '2734', 'Buchberg/Schneeberg'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0621', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'64', 'o_sort': u'62', 'service_text': u'D'})

    def test_difficult_service(self):
        route = self.router.route(Destination('AT', '4240', 'Freistadt Österreich'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0634', 'serviceinfo': '', 'country': u'AT',
                                               'd_sort': u'22', 'o_sort': u'62', 'service_text': u'D'})
        route = self.router.route(Destination('AT', '5101', 'Bergheim bei Salzburg'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0625', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'2509', 'o_sort': u'62', 'service_text': u'D'})
        route = self.router.route(Destination('AT', '8230', 'Hartberg'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0628', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'1290', 'o_sort': u'62', 'service_text': u'D'})
        route = self.router.route(Destination('AT', '8045', 'Graz/<C3><96>sterreich'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0628', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'2840', 'o_sort': u'62', 'service_text': u'D'})

    def test_postcode_with_country(self):
        route = self.router.route(Destination(postcode='FR-66400', country='FR'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0470', 'serviceinfo': '', 'country': u'FR',
                                               'd_sort': u'U53', 'o_sort': u'16', 'service_text': u'D'})
        route = self.router.route(Destination(postcode='FR 66400', country='FR'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0470', 'serviceinfo': '', 'country': u'FR',
                                               'd_sort': u'U53', 'o_sort': u'16', 'service_text': u'D'})
        route = self.router.route(Destination(postcode='FR66400', country='FR'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0470', 'serviceinfo': '', 'country': 'FR',
                                               'd_sort': 'U53', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination(postcode='F-66400', country='FR'))
        self.assertDicEq(route.routingdata(), {'d_depot': '0470', 'serviceinfo': '', 'country': 'FR',
                                               'd_sort': 'U53', 'o_sort': '16', 'service_text': 'D'})

    def test_postcode_spaces(self):
        route = self.router.route(Destination(postcode='42 477'))
        self.assertDicEq(route.routingdata(), {'o_sort': '42', 'serviceinfo': '', 'country': 'DE',
                                               'd_sort': '65', 'd_depot': '0142', 'service_text': 'D'})
        route = self.router.route(Destination(postcode=' 42477'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0142', 'serviceinfo': '', 'country': u'DE',
                                               'd_sort': u'65', 'o_sort': u'42', 'service_text': u'D'})
        route = self.router.route(Destination(postcode=' 42477 '))
        self.assertDicEq(route.routingdata(), {'d_depot': '0142', 'serviceinfo': '', 'country': 'DE',
                                               'd_sort': '65', 'o_sort': '42', 'service_text': 'D'})
        # real live sample
        route = self.router.route(Destination('GB', 'GU148HN', 'Hampshire'))
        self.assertDicEq(route.routingdata(), {'d_depot': '1550', 'serviceinfo': '', 'country': 'GB',
                                               'd_sort': '', 'o_sort': '52', 'service_text': 'D'})
        route = self.router.route(Destination('GB', 'GU 14 8HN', 'Hampshire'))
        self.assertDicEq(route.routingdata(), {'d_depot': '1550', 'serviceinfo': '', 'country': 'GB',
                                               'd_sort': '', 'o_sort': '52', 'service_text': 'D'})

    def test_problematic_routes(self):
        # Lichtenstein is problematic because usually it is routed trough Swizerland.
        route = self.router.route(Destination('LI', '8440'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0617', 'serviceinfo': '', 'country': u'CH',
                                               'd_sort': u'', 'o_sort': u'78', 'service_text': u'D'})
        route = self.router.route(Destination('LI', '8440', 'Steinfort'))
        self.assertDicEq(route.routingdata(), {'d_depot': u'0617', 'serviceinfo': '', 'country': u'CH',
                                               'd_sort': u'', 'o_sort': u'78', 'service_text': u'D'})

    def test_international(self):
        # AR   | 1426  | Buenos Aire
        self.assertDicEq(get_route('AR', '1426').routingdata(),
            {'d_depot': u'0920', 'serviceinfo': u'', 'country': u'AR', 'd_sort': u'', 'o_sort': u'16',
             'service_text': u'D'})
        # AZ   | 1073 | Baku
        self.assertDicEq(get_route('AZ', '1073').routingdata(),
            {'d_depot': u'0918', 'serviceinfo': '', 'country': 'AZ', 'd_sort': u'CDG', 'o_sort': u'16',
             'service_text': u'D'})
        # BE   | 3960 | Bree/Belgien
        self.assertDicEq(get_route('BE', '3960').routingdata(),
            {'d_depot': u'0532', 'serviceinfo': u'', 'country': u'BE', 'd_sort': u'A353', 'o_sort': u'52',
            'service_text': u'D'})
        # BG   | 1766 | Sofia
        self.assertDicEq(get_route('BG', '1766').routingdata(),
            {'d_depot': u'1670', 'serviceinfo': '', 'country': u'BG', 'd_sort': u'1712', 'o_sort': u'62', 'service_text': u'D'})
        # CH   | 3601 | Thun/Schweiz
        self.assertDicEq(get_route('CH', '3601').routingdata(),
            {'d_depot': u'0612', 'serviceinfo': u'', 'country': u'CH', 'd_sort': u'', 'o_sort': u'78',
            'service_text': u'D'})
        # CZ   | 16300 | Praha 6- Repy
        self.assertDicEq(get_route('CZ', '16300').routingdata(),
            {'d_depot': u'1391', 'serviceinfo': u'', 'country': u'CZ', 'd_sort': u'844', 'o_sort': u'10',
            'service_text': u'D'})
        # CZ   | 71000 | Ostrava
        self.assertDicEq(get_route('CZ', '71000').routingdata(),
            {'d_depot': u'1384', 'serviceinfo': u'', 'country': u'CZ', 'd_sort': u'412', 'o_sort': u'10',
            'service_text': u'D'})
        # DE   | 04316 | Leipzig
        self.assertDicEq(get_route('DE', '04316').routingdata(),
            {'d_depot': u'0104', 'serviceinfo': '', 'country': u'DE', 'd_sort': u'3MEN', 'o_sort': u'10',
             'service_text': u'D'})
        # DE   | 99974 | M<C3><BC>hlhausen / Th<C3><BC>ringen
        self.assertDicEq(get_route('DE', '99974').routingdata(),
            {'d_depot': u'0234', 'serviceinfo': u'', 'country': u'DE', 'd_sort': u'C015', 'o_sort': u'KK02',
            'service_text': u'D'})
        # DK   | 4000  | Roskilde
        self.assertDicEq(get_route('DK', '4000').routingdata(),
            {'d_depot': u'0500', 'serviceinfo': u'', 'country': u'DK', 'd_sort': u'01', 'o_sort': u'20',
            'service_text': u'D'})
        # DK   | 9500   | Hobro
        self.assertDicEq(get_route('DK', '9500').routingdata(),
            {'d_depot': u'0504', 'serviceinfo': u'', 'country': u'DK', 'd_sort': u'405', 'o_sort': u'20',
            'service_text': u'D'})
        # EE   | 10621  | Tallinn
        self.assertDicEq(get_route('EE', '10621').routingdata(),
            {'d_depot': u'0560', 'serviceinfo': u'', 'country': u'EE', 'd_sort': u'0005', 'o_sort': u'13',
            'service_text': u'D'})
        # ES   | 08227  | Terrassa
        self.assertDicEq(get_route('ES', '08227').routingdata(),
            {'d_depot': u'0708', 'serviceinfo': u'', 'country': u'ES', 'd_sort': u'01', 'o_sort': u'16',
            'service_text': u'D'})
        # FI   | 94700  | Kemi
        self.assertDicEq(get_route('FI', '94700').routingdata(),
            {'d_depot': u'1614', 'serviceinfo': u'', 'country': u'FI', 'd_sort': u'505', 'o_sort': u'15',
            'service_text': u'D'})
        # FR   | 91044  | EVRY-LISSES
        self.assertDicEq(get_route('FR', '91044').routingdata(),
            {'d_depot': u'0408', 'serviceinfo': '', 'country': u'FR', 'd_sort': u'S61', 'o_sort': u'50',
             'service_text': u'D'})
        # GB   | BT387AR              | Carrickfergus
        self.assertDicEq(get_route('GB', 'BT387AR').routingdata(),
            {'d_depot': u'1598', 'serviceinfo': u'', 'country': u'GB', 'd_sort': u'', 'o_sort': u'52',
            'service_text': u'D'})
        # GB   | CB13SW               | Cambridge
        self.assertDicEq(get_route('GB', 'CB13SW').routingdata(),
            {'d_depot': u'1550', 'serviceinfo': u'', 'country': u'GB', 'd_sort': u'', 'o_sort': u'52',
            'service_text': u'D'})
        # GB   | G43 2DX              | Glasgow
        self.assertDicEq(get_route('GB', 'G43 2DX').routingdata(),
            {'d_depot': u'1550', 'serviceinfo': u'', 'country': u'GB', 'd_sort': u'', 'o_sort': u'52',
            'service_text': u'D'})
        # GB   | G432DX               | Glasgow
        self.assertDicEq(get_route('GB', 'G432DX').routingdata(),
            {'d_depot': u'1550', 'serviceinfo': u'', 'country': u'GB', 'd_sort': u'', 'o_sort': u'52',
            'service_text': u'D'})
        # GB   | N41NR                | London
        self.assertDicEq(get_route('GB', 'N41NR').routingdata(),
            {'d_depot': u'1550', 'serviceinfo': u'', 'country': u'GB', 'd_sort': u'', 'o_sort': u'52',
            'service_text': u'D'})
        # GR   | 17341  | Athens
        self.assertDicEq(get_route('GR', '17341').routingdata(),
            {'d_depot': u'1900', 'serviceinfo': u'', 'country': u'GR', 'd_sort': u'', 'o_sort': u'62',
            'service_text': u'D'})
        # GR   | 64200  | Chrisoupoli-KAVALA
        self.assertDicEq(get_route('GR', '64200').routingdata(),
            {'d_depot': u'1948', 'serviceinfo': u'', 'country': u'GR', 'd_sort': u'', 'o_sort': u'62',
            'service_text': u'D'})
        # HR   | 10000 | Zagreb
        self.assertDicEq(get_route('HR', '10000').routingdata(),
            {'d_depot': u'1750', 'serviceinfo': u'', 'country': u'HR', 'd_sort': u'SVI', 'o_sort': u'62',
            'service_text': u'D'})
        # HR   | 44000 | Sisak
        self.assertDicEq(get_route('HR', '44000').routingdata(),
            {'d_depot': u'1750', 'serviceinfo': u'', 'country': u'HR', 'd_sort': u'020', 'o_sort': u'62',
            'service_text': u'D'})
        # HU   | 1121  | Budapest
        self.assertDicEq(get_route('HU', '1121').routingdata(),
            {'d_depot': u'1640', 'serviceinfo': u'', 'country': u'HU', 'd_sort': u'027', 'o_sort': u'62',
            'service_text': u'D'})
        # HU   | 9400  | Sopron
        self.assertDicEq(get_route('HU', '9400').routingdata(),
            {'d_depot': u'1646', 'serviceinfo': u'', 'country': u'HU', 'd_sort': u'663', 'o_sort': u'62',
            'service_text': u'D'})
        # IT   | 34100    | Trieste / Italien
        self.assertDicEq(get_route('IT', '34100').routingdata(),
            {'d_depot': u'0835', 'serviceinfo': u'', 'country': u'IT', 'd_sort': u'01', 'o_sort': u'16',
            'service_text': u'D'})
        # LI   | 09494    | Schaan
        self.assertDicEq(get_route('LI', '09494').routingdata(),
            {'d_depot': u'0617', 'serviceinfo': u'', 'country': u'CH', 'd_sort': u'', 'o_sort': u'78',
            'service_text': u'D'})
        # LI   | 9999     | Wemperhardt
        self.assertDicEq(get_route('LI', '9999').routingdata(),
            {'d_depot': u'0617', 'serviceinfo': u'', 'country': u'CH', 'd_sort': u'', 'o_sort': u'78',
            'service_text': u'D'})
        # LI   | CH-9491  | Ruggell
        self.assertDicEq(get_route('LI', 'CH-9491').routingdata(),
            {'d_depot': u'0617', 'serviceinfo': u'', 'country': u'CH', 'd_sort': u'', 'o_sort': u'78',
            'service_text': u'D'})
        # LI   | 9491  | Ruggell
        self.assertDicEq(get_route('LI', '9491').routingdata(),
            {'d_depot': u'0617', 'serviceinfo': u'', 'country': u'CH', 'd_sort': u'', 'o_sort': u'78',
            'service_text': u'D'})
        # LT   | 3031     | Kaunas
        self.assertDicEq(get_route('LT', '3031').routingdata(),
            {'d_depot': u'0594', 'serviceinfo': '', 'country': u'LT', 'd_sort': u'732', 'o_sort': u'13',
             'service_text': u'D'})
        # LV   | 1039     | Riga
        self.assertDicEq(get_route('LV', '1039').routingdata(),
            {'d_depot': u'0575', 'serviceinfo': u'', 'country': u'LV', 'd_sort': u'R39', 'o_sort': u'13',
            'service_text': u'D'})
        # NL   | 7443TC   | Nijverdal
        self.assertDicEq(get_route('NL', '7443TC').routingdata(),
            {'d_depot': u'0512', 'serviceinfo': '', 'country': u'NL', 'd_sort': u'B535', 'o_sort': u'52',
             'service_text': u'D'})
        # NL   | 9405 JB  | Assen
        self.assertDicEq(get_route('NL', '9405 JB').routingdata(),
            {'d_depot': u'0513', 'serviceinfo': u'', 'country': u'NL', 'd_sort': u'421', 'o_sort': u'52',
            'service_text': u'D'})
        # NO   | 6800     | Förde
        self.assertDicEq(get_route('NO', '6800').routingdata(),
            {'d_depot': u'0360', 'serviceinfo': u'', 'country': u'NO', 'd_sort': u'01', 'o_sort': u'15',
            'service_text': u'D'})
        # PL   | 80516    | Gdansk
        self.assertDicEq(get_route('PL', '80516').routingdata(),
            {'d_depot': u'1306', 'serviceinfo': u'', 'country': u'PL', 'd_sort': u'', 'o_sort': u'13',
            'service_text': u'D'})
        # PL   | 22300    | Krasnystaw
        self.assertDicEq(get_route('PL', '22300').routingdata(),
            {'d_depot': u'1300', 'serviceinfo': u'', 'country': u'PL', 'd_sort': u'', 'o_sort': u'13',
            'service_text': u'D'})
        # SE   | 11358    | Stockholm
        self.assertDicEq(get_route('SE', '11358').routingdata(),
            {'d_depot': u'0312', 'serviceinfo': u'', 'country': u'SE', 'd_sort': u'01', 'o_sort': u'20',
            'service_text': u'D'})
        # SE   | 75752    | Uppsala
        self.assertDicEq(get_route('SE', '75752').routingdata(),
            {'d_depot': u'0312', 'serviceinfo': u'', 'country': u'SE', 'd_sort': u'01', 'o_sort': u'20',
            'service_text': u'D'})
        # SI   | 1225     | Lukovica
        self.assertDicEq(get_route('SI', '1225').routingdata(),
            {'d_depot': u'1696', 'serviceinfo': '', 'country': u'SI', 'd_sort': u'14', 'o_sort': u'62',
             'service_text': u'D'})
        # SK   | 82105    | Bratislava
        self.assertDicEq(get_route('SK', '82105').routingdata(),
            {'d_depot': u'0661', 'serviceinfo': '', 'country': u'SK', 'd_sort': u'10', 'o_sort': u'10',
             'service_text': u'D'})

    def test_incorrectCountry(self):
        self.assertRaises(CountryError, get_route, 'URG', '42477')

    def test_incorrectLocation(self):
        self.assertRaises(TranslationError, get_route, 'DE', None)

    def test_incorrectService(self):
        self.assertRaises(ServiceError, get_route, 'DE', '0001')

    def test_select_routes(self):
        self.router.conditions = ['1=1']
        rows = self.router.select_routes('DestinationCountry=?', ('UZ', ))
        self.assert_(len(rows) > 0)

    def test_cache(self):
        self.assertDicEq(vars(get_route('LI', '8440')), vars(get_route_without_cache('LI', '8440')))


class HighLevelTest(TestCase):

    def test_get_route(self):
        self.assertDicEq(vars(get_route('DE', '42897')),
            {'service_mark': u'', 'o_sort': u'42', 'serviceinfo': u'', 'barcode_id': u'37',
             'grouping_priority': u'', 'country': u'DE', 'countrynum': u'276',
             'routingtable_version': u'20100503', 'iata_code': u'', 'd_sort': u'15',
             'postcode': u'42897', 'd_depot': u'0142', 'service_text': u'D'})
        self.assertDicEq(vars(get_route('DE', '42897', 'Remscheid')),
            {'service_mark': u'', 'o_sort': u'42', 'serviceinfo': u'', 'barcode_id': u'37',
             'grouping_priority': u'', 'country': u'DE', 'countrynum': u'276',
             'routingtable_version': u'20100503', 'iata_code': u'', 'd_sort': u'15',
             'postcode': u'42897', 'd_depot': u'0142', 'service_text': u'D'})
        self.assertDicEq(vars(get_route('DE', '42897', 'Remscheid', '101')),
            {'service_mark': u'', 'o_sort': u'42', 'serviceinfo': u'', 'barcode_id': u'37',
             'grouping_priority': u'', 'country': u'DE', 'countrynum': u'276',
             'routingtable_version': u'20100503', 'iata_code': u'', 'd_sort': u'15',
             'postcode': u'42897', 'd_depot': u'0142', 'service_text': u'D'})
        self.assertDicEq(vars(get_route('LI', '8440')),
            {'service_mark': u'', 'o_sort': u'78', 'serviceinfo': u'', 'barcode_id': u'37',
             'grouping_priority': u'', 'country': u'CH', 'countrynum': u'756',
             'routingtable_version': u'20100503', 'iata_code': u'', 'd_sort': u'',
             'postcode': u'8440', 'd_depot': u'0617', 'service_text': u'D'})
        self.assertDicEq(vars(get_route(u'LI', '8440')),
            {'service_mark': u'', 'o_sort': u'78', 'serviceinfo': u'', 'barcode_id': u'37',
             'grouping_priority': u'', 'country': u'CH', 'countrynum': u'756',
             'routingtable_version': u'20100503', 'iata_code': u'', 'd_sort': u'',
             'postcode': u'8440', 'd_depot': u'0617', 'service_text': u'D'})
        self.assertDicEq(vars(get_route(u'LI', u'8440')),
            {'service_mark': u'', 'o_sort': u'78', 'serviceinfo': u'', 'barcode_id': u'37',
             'grouping_priority': u'', 'country': u'CH', 'countrynum': u'756',
             'routingtable_version': u'20100503', 'iata_code': u'', 'd_sort': u'',
             'postcode': u'8440', 'd_depot': u'0617', 'service_text': u'D'})

    def test_cache(self):
        self.assertEqual(vars(get_route('LI', '8440')), vars(get_route_without_cache('LI', '8440')))

if __name__ == '__main__':
    start = time.time()
    router = Router(RouteData())
    stamp = time.time()
    router.route(Destination('AT', '4240', 'Freistadt Österreich')).routingdata()
    end = time.time()
    # print ("took %.3fs to find a single route (including %.3fs initialisation overhead)"
    #        % (end-start, stamp-start))

    unittest.main()
