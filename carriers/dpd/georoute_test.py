#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Test routing resolver for DPD. Coded by jmv"""

import os, time
import unittest

import os, os.path, logging
import sqlite3
        
from georoute import *


class RouteDataTest(unittest.TestCase):
    def setUp(self):
        self.data = RouteData()
        self.db = self.data.db
        
    def test_version(self):
        self.assertEqual(self.data.version, '20070102')

    def test_get_country(self):
        self.assertRaises(CountryError, self.data.get_countrynum, 'URW')
        self.assertEqual(self.data.get_countrynum('JP'), '392')
        self.assertEqual(self.data.get_countrynum('DE'), '276')
        self.assertEqual(self.data.get_countrynum('de'), '276')

    def test_read_depots(self):
        c = self.db.cursor()
        c.execute("""SELECT * FROM depots WHERE DepotNumber=?""", ('0015',))
        rows = c.fetchall()
        self.assertEqual(1, len(rows))
        self.assertEqual(('0015', '', 'EDED,EFDX', 'Betriebsgesellschaft DPD Deutscher',
                          '', 'Otto-Hahn-Strasse 5', '', '59423', 'Unna', 'DE',
                          '+49-(0) 23 03-8 88-0', '+49-(0) 23 03-8 88-31', '', ''),
                         rows[0])

    def test_expand_depots(self):
        c = self.db.cursor()
        c.execute("""SELECT id
                     FROM routes
                     WHERE DestinationCountry='DE' AND BeginPostCode='42477'""")
        rows = c.fetchall()
        self.assertEqual(1, len(rows))
        route = rows[0][0]
        c.execute("SELECT depot FROM routedepots WHERE route=?", (route,))
        rows = c.fetchall()
        self.assertEqual(1, len(rows))

    def test_get_service(self):
        self.assertEqual(self.data.get_service('180'), ('180', 'AM1-NO', '', '022,160', ''))
        self.assertRaises(ServiceError, self.data.get_service, '100000')

    def test_get_servicetext(self):
        text = self.data.get_servicetext('185')
        self.assertEqual('DPD EXPRESS10 Unfrei / ex works', text)

    def test_translate_location(self):
        self.assertEqual('1', self.data.translate_location('Dublin', 'IE'))
        self.assertRaises(TranslationError, self.data.translate_location, 'Cahir', 'IE')

    def test_read_routes(self):
        c = self.db.cursor()
        c.execute("""SELECT *
                     FROM routes
                     WHERE DestinationCountry='DE' AND BeginPostCode='00001' AND EndPostCode='99999'""")
        rows = c.fetchall()
        self.assertEqual(2, len(rows))
        self.assertEqual(('299,302,303', 'GEALT,GEAFR,GEDOM', '', '50', '0456', '9', '', '37'),
                         rows[0][4:])


class RouterTest(unittest.TestCase):
    def setUp(self):
        self.data = RouteData()
        self.router = Router(self.data)

    def test_route(self):
        parcel = Parcel('0142', '101', 'DE', None, '42477')
        route = self.router.route(parcel)
        self.assertEqual('0142', route.d_depot)
        self.assertEqual('65', route.d_sort)
        self.assertEqual('37', route.barcode_id)
        self.assertEqual('D', route.service_text)
        self.assertEqual('DE', route.country)
        self.assertEqual('', route.serviceinfo)

        parcel = Parcel('0966', '302', 'PT', None, '8500340')
        route = self.router.route(parcel)
        self.assertEqual('0966', route.d_depot)
        self.assertEqual('FPTM', route.d_sort)
        self.assertEqual('4', route.grouping_priority)
        self.assertEqual('37', route.barcode_id)
        self.assertEqual('IE2', route.service_text)
        self.assertEqual('E', route.service_mark)
        self.assertEqual('FAO', route.iata_code)
        self.assertEqual('PT', route.country)
        self.assertEqual('DPD EXPRESSInternational', route.serviceinfo)

    def test_known_routes_de(self):
        route = self.router.route(Destination(postcode='42477'))
        self.assertEqual(route.routingdata(), {'d_depot': '0142', 'serviceinfo': '', 'country': 'DE', 
                                               'd_sort': '65', 'o_sort': '42', 'service_text': 'D'})
        route = self.router.route(Destination(postcode='42897'))
        self.assertEqual(route.routingdata(), {'d_depot': '0142', 'serviceinfo': '', 'country': 'DE',
                                               'd_sort': '15', 'o_sort': '42', 'service_text': 'D'})
        route = self.router.route(Destination(postcode='53111'))
        self.assertEqual(route.routingdata(), {'d_depot': '0150', 'serviceinfo': '', 'country': 'DE', 
                                               'd_sort': '62', 'o_sort': '50', 'service_text': 'D'})
        route = self.router.route(Destination(postcode='53111', country='DE'))
        self.assertEqual(route.routingdata(), {'d_depot': '0150', 'serviceinfo': '', 'country': 'DE', 
                                               'd_sort': '62', 'o_sort': '50', 'service_text': 'D'})
        route = self.router.route(Destination('DE', '53111'))
        self.assertEqual(route.routingdata(), {'d_depot': '0150', 'serviceinfo': '', 'country': 'DE', 
                                               'd_sort': '62', 'o_sort': '50', 'service_text': 'D'})
        route = self.router.route(Destination('DE', '53111', city='Bonn'))
        self.assertEqual(route.routingdata(), {'d_depot': '0150', 'serviceinfo': '', 'country': 'DE', 
                                               'd_sort': '62', 'o_sort': '50', 'service_text': 'D'})
        route = self.router.route(Destination('DE', '53111', 'Bonn'))
        self.assertEqual(route.routingdata(), {'d_depot': '0150', 'serviceinfo': '', 'country': 'DE', 
                                               'd_sort': '62', 'o_sort': '50', 'service_text': 'D'})

    def test_known_routes_world(self):
        route = self.router.route(Destination(postcode='66400', country='FR'))
        self.assertEqual(route.routingdata(), {'d_depot': '0470', 'serviceinfo': '', 'country': 'FR', 
                                               'd_sort': 'U53', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination('FR', '66400', 'Ceret'))
        self.assertEqual(route.routingdata(), {'d_depot': '0470', 'serviceinfo': '', 'country': 'FR', 
                                               'd_sort': 'U53', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination('BE', '3960', 'Bree/Belgien'))
        self.assertEqual(route.routingdata(), {'d_depot': '0532', 'serviceinfo': '', 'country': 'BE', 
                                               'd_sort': '53', 'o_sort': '52', 'service_text': 'D'})
        route = self.router.route(Destination('CH', '6005', 'Luzern'))
        self.assertEqual(route.routingdata(), {'d_depot': '0616', 'serviceinfo': '', 'country': 'CH', 
                                              'd_sort': '40', 'o_sort': '78', 'service_text': 'D'})
        
        route = self.router.route(Destination('AT', '1210', 'Wien'))
        self.assertEqual(route.routingdata(), {'d_depot': '0622', 'serviceinfo': '', 'country': 'AT', 
                                               'd_sort': '10', 'o_sort': '62', 'service_text': 'D'})
        route = self.router.route(Destination('AT', '4820', 'Bad Ischl'))
        self.assertEqual(route.routingdata(), {'d_depot': '0624', 'serviceinfo': '', 'country': 'AT',
                                               'd_sort': '63', 'o_sort': '62', 'service_text': 'D'})
        route = self.router.route(Destination('AT', '7400', 'Oberwart'))
        self.assertEqual(route.routingdata(), {'d_depot': '0628', 'serviceinfo': '', 'country': 'AT',
                                               'd_sort': '01', 'o_sort': '62', 'service_text': 'D'})
        route = self.router.route(Destination('AT', '4400', 'Steyr'))
        self.assertEqual(route.routingdata(), {'d_depot': '0624', 'serviceinfo': '', 'country': 'AT',
                                               'd_sort': '70', 'o_sort': '62', 'service_text': 'D'})
        route = self.router.route(Destination('AT', '1220', 'Wien'))
        self.assertEqual(route.routingdata(), {'d_depot': '0622', 'serviceinfo': '', 'country': 'AT',
                                               'd_sort': '30', 'o_sort': '62', 'service_text': 'D'})
        route = self.router.route(Destination('AT', '6890', 'Lustenau'))
        self.assertEqual(route.routingdata(), {'d_depot': '0627', 'serviceinfo': '', 'country': 'AT',
                                               'd_sort': '01', 'o_sort': '62', 'service_text': 'D'})
        route = self.router.route(Destination('BE', '3520', 'ZONHOVEN'))
        self.assertEqual(route.routingdata(), {'d_depot': '0530', 'serviceinfo': '', 'country': 'BE',
                                               'd_sort': '94', 'o_sort': '52', 'service_text': 'D'})
        route = self.router.route(Destination('BE', '4890', 'Thimister'))
        self.assertEqual(route.routingdata(), {'d_depot': '0532', 'serviceinfo': '', 'country': 'BE',
                                               'd_sort': '91', 'o_sort': '52', 'service_text': 'D'})
        route = self.router.route(Destination('CH', '8305', 'Dietlikon'))
        self.assertEqual(route.routingdata(), {'d_depot': '0615', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': '77', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('CH', '4051', 'Basel'))
        self.assertEqual(route.routingdata(), {'d_depot': '0610', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': '10', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('CH', '8808', 'Pf<C3><A4>ffikon'))
        self.assertEqual(route.routingdata(), {'d_depot': '0616', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': '04', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('DK', '9500', 'Hobro'))
        self.assertEqual(route.routingdata(), {'d_depot': '0504', 'serviceinfo': '', 'country': 'DK',
                                               'd_sort': '05', 'o_sort': '20', 'service_text': 'D'})
        # Lichtenstein is routed via CH
        route = self.router.route(Destination('LI', '8399', 'Windhof / Luxembourg'))
        self.assertEqual(route.routingdata(), {'d_depot': '0617', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': '', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('LI', '9495', 'Triesen'))
        self.assertEqual(route.routingdata(), {'d_depot': '0617', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': '', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('LI', '8440', 'Steinfort'))
        self.assertEqual(route.routingdata(), {'d_depot': '0617', 'serviceinfo': '', 'country': 'CH',
                                               'd_sort': '', 'o_sort': '78', 'service_text': 'D'})
        route = self.router.route(Destination('NL', '2742', 'RD Waddinxveen'))
        self.assertEqual(route.routingdata(), {'d_depot': '0521', 'serviceinfo': '', 'country': 'NL',
                                               'd_sort': '27', 'o_sort': '52', 'service_text': 'D'})
        route = self.router.route(Destination('NL', '7604', 'BJ Almelo / Niederlande'))
        self.assertEqual(route.routingdata(), {'d_depot': '0512', 'serviceinfo': '', 'country': 'NL',
                                               'd_sort': '14', 'o_sort': '52', 'service_text': 'D'})
        route = self.router.route(Destination('NL', '2742', 'KZ Waddinxveen'))
        self.assertEqual(route.routingdata(), {'d_depot': '0521', 'serviceinfo': '', 'country': 'NL',
                                               'd_sort': '27', 'o_sort': '52', 'service_text': 'D'})
        route = self.router.route(Destination('CZ', '41742', 'Krupka 1'))
        self.assertEqual(route.routingdata(), {'d_depot': '0640', 'serviceinfo': '', 'country': 'CZ',
                                               'd_sort': '21', 'o_sort': '01', 'service_text': 'D'})
        route = self.router.route(Destination('ES', '28802', 'Alcala de Henares (Madrid)'))
        self.assertEqual(route.routingdata(), {'d_depot': '0728', 'serviceinfo': '', 'country': 'ES',
                                               'd_sort': '01', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination('ES', '28010', 'Madrid'))
        self.assertEqual(route.routingdata(), {'d_depot': '0728', 'serviceinfo': '', 'country': 'ES',
                                               'd_sort': '01', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination('FR', '84170', 'MONTEUX'))
        self.assertEqual(route.routingdata(), {'d_depot': '0447', 'serviceinfo': '', 'country': 'FR',
                                               'd_sort': 'S30', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination('FR', '91044', 'Evry Cedex'))
        self.assertEqual(route.routingdata(), {'d_depot': '0408', 'serviceinfo': '', 'country': 'FR',
                                               'd_sort': 'M06', 'o_sort': '50', 'service_text': 'D'})
    
    def test_difficult_routingdepots(self):
        route = self.router.route(Destination('AT', '3626', 'H<C3><BC>nibach'))
        self.assertEqual(route.routingdata(), {'d_depot': u'0918', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'CDG', 'o_sort': u'43', 'service_text': u'D'})
        route = self.router.route(Destination('AT', '8225', 'P<C3><B6>llau'))
        self.assertEqual(route.routingdata(), {'d_depot': u'0918', 'serviceinfo': u'', 'country': 'AT', 
                                               'd_sort': u'CDG', 'o_sort': u'43', 'service_text': u'D'})
        route = self.router.route(Destination('AT', '5020', 'Salzburg'))
        self.assertEqual(route.routingdata(), {'d_depot': u'0918', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'CDG', 'o_sort': u'43', 'service_text': u'D'})
        route = self.router.route(Destination('SE', '65224', 'Karlstad'))
        self.assertEqual(route.routingdata(), {'d_depot': u'0918', 'serviceinfo': u'', 'country': 'SE',
                                               'd_sort': u'CDG', 'o_sort': u'43', 'service_text': u'D'})
        route = self.router.route(Destination('AT', '2734', 'Buchberg/Schneeberg'))
        self.assertEqual(route.routingdata(), {'d_depot': u'0918', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'CDG', 'o_sort': u'43', 'service_text': u'D'})

    def test_difficult_service(self):
        route = self.router.route(Destination('AT', '4240', 'Freistadt Österreich'))
        self.assertEqual(route.routingdata(), {'d_depot': u'0918', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'CDG', 'o_sort': u'43', 'service_text': u'D'})
        route = self.router.route(Destination('AT', '5101', 'Bergheim bei Salzburg'))
        self.assertEqual(route.routingdata(), {'d_depot': u'0918', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'CDG', 'o_sort': u'43', 'service_text': u'D'})
        route = self.router.route(Destination('AT', '8230', 'Hartberg'))
        self.assertEqual(route.routingdata(), {'d_depot': u'0918', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'CDG', 'o_sort': u'43', 'service_text': u'D'})
        route = self.router.route(Destination('AT', '8045', 'Graz/<C3><96>sterreich'))
        self.assertEqual(route.routingdata(), {'d_depot': u'0918', 'serviceinfo': u'', 'country': 'AT',
                                               'd_sort': u'CDG', 'o_sort': u'43', 'service_text': u'D'})
    
    def test_postcode_with_country(self):
        route = self.router.route(Destination(postcode='FR-66400', country='FR'))
        self.assertEqual(route.routingdata(), {'d_depot': '0470', 'serviceinfo': '', 'country': 'FR', 
                                               'd_sort': 'U53', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination(postcode='FR 66400', country='FR'))
        self.assertEqual(route.routingdata(), {'d_depot': '0470', 'serviceinfo': '', 'country': 'FR', 
                                               'd_sort': 'U53', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination(postcode='FR66400', country='FR'))
        self.assertEqual(route.routingdata(), {'d_depot': '0470', 'serviceinfo': '', 'country': 'FR', 
                                               'd_sort': 'U53', 'o_sort': '16', 'service_text': 'D'})
        route = self.router.route(Destination(postcode='F-66400', country='FR'))
        self.assertEqual(route.routingdata(), {'d_depot': '0470', 'serviceinfo': '', 'country': 'FR', 
                                               'd_sort': 'U53', 'o_sort': '16', 'service_text': 'D'})
    
    def test_postcode_spaces(self):
        route = self.router.route(Destination(postcode='42 477'))
        self.assertEqual(route.routingdata(), {'d_depot': '0142', 'serviceinfo': '', 'country': 'DE', 
                                               'd_sort': '65', 'o_sort': '42', 'service_text': 'D'})
        route = self.router.route(Destination(postcode=' 42477'))
        self.assertEqual(route.routingdata(), {'d_depot': '0142', 'serviceinfo': '', 'country': 'DE', 
                                               'd_sort': '65', 'o_sort': '42', 'service_text': 'D'})
        route = self.router.route(Destination(postcode=' 42477 '))
        self.assertEqual(route.routingdata(), {'d_depot': '0142', 'serviceinfo': '', 'country': 'DE', 
                                               'd_sort': '65', 'o_sort': '42', 'service_text': 'D'})
        # real live sample
        route = self.router.route(Destination('GB', 'GU148HN', 'Hampshire'))
        self.assertEqual(route.routingdata(), {'d_depot': '0550', 'serviceinfo': '', 'country': 'GB',
                                               'd_sort': '', 'o_sort': '52', 'service_text': 'D'})
        route = self.router.route(Destination('GB', 'GU 14 8HN', 'Hampshire'))
        self.assertEqual(route.routingdata(), {'d_depot': '0550', 'serviceinfo': '', 'country': 'GB',
                                               'd_sort': '', 'o_sort': '52', 'service_text': 'D'})

    def test_problematic_routes(self):
        route = self.router.route(Destination('LI', '8440'))
        self.assertEqual(route.routingdata(), {'d_depot': u'0617', 'serviceinfo': u'', 'country': u'CH',
                                               'd_sort': u'', 'o_sort': u'78', 'service_text': u'D'})
        route = self.router.route(Destination('LI', '8440', 'Steinfort'))
        self.assertEqual(route.routingdata(), {'d_depot': u'0617', 'serviceinfo': u'', 'country': u'CH',
                                               'd_sort': u'', 'o_sort': u'78', 'service_text': u'D'})


    def test_incorrectCountry(self):
        parcel = Parcel('0142', '101', 'URG', None, '42477')
        self.assertRaises(CountryError, self.router.route, parcel)

    def test_incorrectLocation(self):
        parcel = Parcel('0142', '101', 'DE', 'Berlin', None)
        self.assertRaises(TranslationError, self.router.route, parcel)

    def test_incorrectService(self):
        parcel = Parcel('0142', '901101', 'DE', 'Berlin', '0001')
        self.assertRaises(ServiceError, self.router.route, parcel)

    def test_select_routes(self):
        self.router.conditions = ['1=1']
        rows = self.router.select_routes('DestinationCountry=?', ('UZ',))
        self.assert_(len(rows) > 0)
    

class HighLevelTest(unittest.TestCase):
    def test_find_route(self):
        self.assertEqual(vars(find_route('0142', '101', 'LI', '8440')),
            {'service_mark': u'', 'o_sort': u'78', 'serviceinfo': u'', 'barcode_id': u'37',
             'grouping_priority': u'', 'country': u'CH', 'countrynum': u'756',
             'routingtable_version': u'20070102', 'iata_code': u'', 'd_sort': u'',
             'postcode': u'8440', 'd_depot': u'0617', 'service_text': u'D'})
        self.assertEqual(vars(find_route('0142', '101', u'LI', '8440')),
            {'service_mark': u'', 'o_sort': u'78', 'serviceinfo': u'', 'barcode_id': u'37',
             'grouping_priority': u'', 'country': u'CH', 'countrynum': u'756',
             'routingtable_version': u'20070102', 'iata_code': u'', 'd_sort': u'',
             'postcode': u'8440', 'd_depot': u'0617', 'service_text': u'D'})
        self.assertEqual(vars(find_route(u'0142', u'101', u'LI', u'8440')),
            {'service_mark': u'', 'o_sort': u'78', 'serviceinfo': u'', 'barcode_id': u'37',
             'grouping_priority': u'', 'country': u'CH', 'countrynum': u'756',
             'routingtable_version': u'20070102', 'iata_code': u'', 'd_sort': u'',
             'postcode': u'8440', 'd_depot': u'0617', 'service_text': u'D'})
    
    def test_get_route(self):
        # TODO: dix test, test get_route
        self.assertEqual(vars(get_route('DE', '42897')),
            {'service_mark': u'', 'o_sort': u'42', 'serviceinfo': u'', 'barcode_id': u'37', 
             'grouping_priority': u'', 'country': u'DE', 'countrynum': u'276', 
             'routingtable_version': u'20070102', 'iata_code': u'', 'd_sort': u'15', 
             'postcode': u'42897', 'd_depot': u'0142', 'service_text': u'D'})
        self.assertEqual(vars(get_route('DE', '42897', 'Remscheid')), 
            {'service_mark': u'', 'o_sort': u'42', 'serviceinfo': u'', 'barcode_id': u'37', 
             'grouping_priority': u'', 'country': u'DE', 'countrynum': u'276', 
             'routingtable_version': u'20070102', 'iata_code': u'', 'd_sort': u'15', 
             'postcode': u'42897', 'd_depot': u'0142', 'service_text': u'D'})
        self.assertEqual(vars(get_route('DE', '42897', 'Remscheid', '101')),
            {'service_mark': u'', 'o_sort': u'42', 'serviceinfo': u'', 'barcode_id': u'37', 
             'grouping_priority': u'', 'country': u'DE', 'countrynum': u'276', 
             'routingtable_version': u'20070102', 'iata_code': u'', 'd_sort': u'15', 
             'postcode': u'42897', 'd_depot': u'0142', 'service_text': u'D'})
    
    def test_cache(self):
        self.assertEqual(vars(get_route('LI', '8440')), vars(get_route_without_cache('LI', '8440')))
         
if __name__ == '__main__':
    start = time.time()
    router = Router(RouteData())
    stamp = time.time()
    router.route(Destination('AT', '4240', 'Freistadt Österreich')).routingdata()
    end = time.time()
    print "took %.3fs to find a single route (including %.3fs initialisation overhead)" % (end-start, stamp-start)
    
    unittest.main()
