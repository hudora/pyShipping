#!/usr/bin/env python
# encoding: utf-8
"""
test.py - tests for fortras related functionality

Created by Maximillian Dornseif on 2006-11-19.
You may consider this BSD licensed.
"""

import unittest
from pyshipping.fortras.bordero import _clip, Bordero

_nvecount = 0


class TestPackstueck:

    def __init__(self):
        global _nvecount
        self.gewicht = 160000
        self.nve = '%018d' % (_nvecount)
        _nvecount += 1
        self.trackingnummer = self.nve


class TestLieferung:

    def __init__(self):
        global _nvecount
        self.packstuecke = [TestPackstueck(), TestPackstueck()]
        self.lieferscheinnummer = '123456'
        self.auftragsnummer = '654321'
        self.auftragsnummer_kunde = 'auftragsnummer_kunde'
        self.kundennummer = '54321'
        self.name1 = 'name1-Iñtërnâtiônàlizætiøn-latin1-name1-name1'
        self.name2 = 'name2zulangname2zulangname2zulangname2zulangname2zulangname2zulangname2n'
        self.name3 = 'name3'
        self.name4 = 'nane4'
        self.adresse = 'strassestrassestrassestrassestrassestrassestrasse'
        self.plz = 'plz99999'
        self.ort = 'ortortortortortortortortortortortortortortort'
        self.land = 'DE'
        self.spedition = 'Maeuler'
        self.frankatur = 'frei'
        self.codedata = 'AAAA'
        self.hebebuehne = True
        self.avisieren_unter = '02195-8393'
        self.versandhinweis = 'versandhinweis'
        self.info = 'info'
        self.fixtermin = False
        self.code = 'c0de'
        self.id = _nvecount
        _nvecount += 1

    def _get_gewicht(self):
        return sum([packstueck.gewicht for packstueck in self.packstuecke])
    gewicht = property(_get_gewicht)


class BorderoTests(unittest.TestCase):

    def test_clip(self):
        self.assertEqual(_clip(3, 'ABCDEF'), 'ABC')
        self.assertEqual(_clip(3, 'ABC'), 'ABC')
        self.assertEqual(_clip(5, 'ABC'), 'ABC')
        self.assertEqual(_clip(0, 'ABC'), '')

    def test_bordero(self):
        bordero = Bordero()
        bordero.borderonr = 1
        bordero.add_lieferung(TestLieferung())
        bordero.add_lieferung(TestLieferung())
        bordero.add_lieferung(TestLieferung())
        bordero.generate_dataexport()


# The following tests have an ugly circular dependency to huLOG - this needs fixing

# class StatTests(unittest.TestCase):
#
#     def test_status(self):
#         tesdata = '''@@PHSTAT128 0128003500107 MAEULER HUDORA1
# Q11515     L00000000000000545177124         091071120061106                                                                    5\
# '''
#         stat = Statusmeldung()
#         #stat.parse(tesdata)
#
#         testdata = '''@@PHSTAT128 0128003500107 MAEULER HUDORA1
# Q11515     L00000000000000395176882         054061120061615                  ROLLKARTE 421/6902                                5
# Q11515     L00000000000000385176883         054061120061615                  ROLLKARTE 421/6902                                5
# Q11515     L00000000000000375176884         054061120061615                  ROLLKARTE 421/6902                                5
# Q11515     L00000000000000365176885         054061120061615                  ROLLKARTE 421/6902                                5
# Q11515     L00000000000000355176886         054061120061615                  ROLLKARTE 421/6902                                5
# Q11515     L00000000000000345176887         054061120061615                  ROLLKARTE 421/6902                                5
# Q11515     L00000000000000335176888         054061120061615                  ROLLKARTE 421/6902                                5
# Q11515     L00000000000000325176890         054061120061615                  ROLLKARTE 421/6902                                5
# '''
#         stat.parse(testdata)
#
#         testdata = '''@@PHSTAT128 0128003500107 MAEULER HUDORA1
# Q11515     L00000000000000395176882         012111120061111   UNTERSCHRIFT                                                     5
# Q11515     L00000000000000385176883         012111120061111   UNTERSCHRIFT                                                     5
# Q11515     L00000000000000375176884         012111120061111   UNTERSCHRIFT                                                     5
# Q11515     L00000000000000365176885         012111120061111   UNTERSCHRIFT                                                     5
# Q11515     L00000000000000355176886         012111120061111   UNTERSCHRIFT                                                     5
# Q11515     L00000000000000345176887         012111120061111   UNTERSCHRIFT                                                     5
# Q11515     L00000000000000335176888         012111120061111   UNTERSCHRIFT                                                     5
# Q11515     L00000000000000325176890         012111120061111   UNTERSCHRIFT                                                     5
# '''
#         stat.parse(testdata)
#
#         testdata = '''@@PHSTAT128 0128003500107 MAEULER HUDORA1
# Q11515     L00000000009106405176617         012031120061500   TESTNAME                                                         5
# Q11515     L00000000009109205176618         012031120061501   TESTNAME2                                                        5
# Q11515     L00000000009111205176619         012031120061510   TESTNAME3                                                        5
# '''
#         stat.parse(testdata)
#
#         testdata = '''@@PHSTAT128 0128003500107 MAEULER HUDORA1
# Q11515     L65827812        5178928         054171120060745                                                                    5
# Q11515     L65827812        5178928         012171120060827   THOMA                                                            5
# Q11515     L232740          5178930         054171120060922                                                                    5
# '''
#         stat.parse(testdata)
#
#         testdata = '''@@PHSTAT128 0128003500107 MAEULER HUDORA1
# Q11515     L6350706         5178934         054171120060726                                                                    5
# Q11515     L6350706         5178934         012171120060911   PATER                                                            5
# '''
#         stat.parse(testdata)
#
#
# class EntlTests(unittest.TestCase):
#
#     def test_entladebericht(self):
#         entl = Entladebericht()
#
#         testdata = '''@@PHENTL128 0128003500107 MAEULER HUDORA1
# M0000000000000000000311200611515     301218990000  301218990000301218990000                                                    5
# W                                                                                                                    EM        5
# N00000000000000000000100000000009106405176617         000                                    0000
# N00000000000000000000200000000009109205176618         000                                    0000
# N00000000000000000000300000000009111205176619         000                                    0000
# '''
#         entl.parse(testdata)
#
#         tesdata = '''@@PHENTL128 0128003500107 MAEULER HUDORA1
# M0000000000000000081611200611515     161120061300  161120061300161120061310                                                    5
# W                                                                                                                    EM        5
# V0000000000000000080000000000000074   00340059980000001166               0                          16112006184200
# '''
#         entl.parse(testdata)
#
#         testdata = '''@@PHENTL128 0128003500107 MAEULER HUDORA1
# M0000000000000000091711200611515     171120061300  171120061310171120061320                                                    5
# W                                                                                                                    EM        5
# V0000000000000000090000000000000104   00340059980000001470               0                          17112006133900
# V0000000000000000090000000000000103   00340059980000001463               0                          17112006134000
# V0000000000000000090000000000000102   00340059980000001456               0                          17112006133900
# V0000000000000000090000000000000101   00340059980000001449               0                          17112006133900
# V0000000000000000090000000000000100   00340059980000001432               0                          17112006134000
# V0000000000000000090000000000000099   00340059980000001425               0                          17112006133900
# V0000000000000000090000000000000098   00340059980000001418               0                          17112006133900
# V0000000000000000090000000000000097   00340059980000001401               0                          17112006133900
# V0000000000000000090000000000000096   00340059980000001395               0                          17112006133900
# V0000000000000000090000000000000095   00340059980000001388               0                          17112006133900
# V0000000000000000090000000000000094   00340059980000001371               0                          17112006134000
# V0000000000000000090000000000000093   00340059980000001364               0                          17112006134000
# V0000000000000000090000000000000092   00340059980000001357               0                          17112006134000
# V0000000000000000090000000000000091   00340059980000001340               0                          17112006134000
# V0000000000000000090000000000000090   00340059980000001333               0                          17112006134000
# V0000000000000000090000000000000089   00340059980000001326               0                          17112006133900
# V0000000000000000090000000000000088   00340059980000001319               0                          17112006133900
# '''
#         entl.parse(testdata)
#
#         testdata = '''@@PHENTL128 0128003500107 MAEULER HUDORA1
# M0000000000000000081611200611515     161120061300  161120061300161120061310                                                    5
# W                                                                                                                    EM        5
# V0000000000000000080000000000000084   00340059980000001272               0                          16112006184200
# V0000000000000000080000000000000083   00340059980000001265               0                          16112006142912
# V0000000000000000080000000000000082   00340059980000001258               0                          16112006184200
# V0000000000000000080000000000000081   00340059980000001241               0                          16112006142913
# V0000000000000000080000000000000080   00340059980000001234               0                          16112006142913
# V0000000000000000080000000000000079   00340059980000001227               0                          16112006142913
# V0000000000000000080000000000000078   00340059980000001210               0                          16112006142913
# V0000000000000000080000000000000077   00340059980000001203               0                          16112006142914
# V0000000000000000080000000000000076   00340059980000001197               0                          16112006184200
# V0000000000000000080000000000000075   00340059980000001180               0                          16112006142914
# V0000000000000000080000000000000074   00340059980000001173               0                          16112006184200
# V461               720-00             00340498430009431112               0                          19092008183100
# '''
#         entl.parse(testdata)
#
if __name__ == '__main__':
    unittest.main()
