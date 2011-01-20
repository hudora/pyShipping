#!/usr/bin/env python
# encoding: utf-8
"""
sendung.py - Sendungsaufteilung - dies definiert eine abstrakte Sendung, mit Packstücken usw. und
             Operationen darauf.

Created by Maximillian Dornseif on 2007-07-11. Based on code from 2007-04-17.
Copyright (c) 2007 HUDORA GmbH. All rights reserved.
"""

import unittest
import math


class AbstractPackstueck(object):
    """Definiert ein Packstück, d.h. eine Versandeinheit. In der Regel eine Palette oder ein Karton"""
    pass


class AbstractItem(object):
    """Definiert ein Sendungsposition. In der Regel definiert als Artikel und Menge."""
    # Kann in der Theorie aus mehreren Packstücken bestehen, das ist aber noch nicht implementeirt.
    def __init__(self):
        # Wir gehen davon aus, dass folgende Attribute von ausserhalb oder von abgeleiteten Klassen
        # definiert wird:
        #self.gewicht_pro_exportkarton = None
        #self.palettenfaktor = None
        #self.produkte_pro_exportkarton = None
        #self.einzelvolumen = None
        #self.einzelgewicht = None
        self.menge = None

    def __unicode__(self):
        if hasattr(self, 'liefertermin') and hasattr(self, 'artnr'):
            return u"%d x %s, %s" % (self.menge, self.artnr, self.liefertermin)
        if hasattr(self, 'artnr'):
            return u"%d x %s" % (self.menge, self.artnr)
        return u"%d x ?????" % (self.menge)

    @property
    def anbruch(self):
        """Returns True if this Item does not result in an export_package to be opened."""
        return (self.menge % self.produkte_pro_exportkarton) != 0

    @property
    def volumen(self):
        """Retuns the volume of this item in m^3."""
        # TODO: Exportkartonvolumen
        return self.menge * self.einzelvolumen

    @property
    def gewicht(self):
        """Retuns the weight of this item in g."""
        # TODO: Exportkartongewicht usw.
        return self.menge * self.einzelgewicht

    @property
    def max_packstueck_gewicht(self):
        """Returns the weigtht of the most heavy box for ths item."""
        if self.menge >= self.produkte_pro_exportkarton:
            return self.gewicht_pro_exportkarton
        return (self.gewicht_pro_exportkarton / self.produkte_pro_exportkarton) * self.menge

    @property
    def paletten(self):
        """Returns the number of pallets of this Item."""
        return float(self.menge) / float(self.palettenfaktor)

    @property
    def picks(self):
        """Returns the number storage locations to be accessed to get the item."""
        picks = self.paletten
        # round up
        if picks != int(picks):
            picks = int(picks + 1)
        return picks

    @property
    def export_kartons(self):
        """Returns the number of export packages needed to fullfill this item as a float."""
        return self.menge / float(self.produkte_pro_exportkarton)

    @property
    def export_karton_gewichte(self):
        """Returns the weights of the estimated number of packages which will be shipped in gramms."""
        menge = self.menge
        ret = []
        while menge:
            if menge > self.produkte_pro_exportkarton:
                ret.append(self.gewicht_pro_exportkarton)
                menge -= self.produkte_pro_exportkarton
            else:
                ret.append(menge * self.einzelgewicht)
                menge = 0
        return ret

    @property
    def packstuecke(self):
        """Returns the absolute number of packages to fullfill this item as an integer.

        This could take into account that packages can be bundled etc.
        """

        packstuecke = self.export_kartons
        # round up
        if packstuecke != int(packstuecke):
            packstuecke = int(packstuecke + 1)
        return int(packstuecke)


class AbstractLieferung(object):
    """Definiert eine Lieferung. Das ist eine Einheit aus Positionen und Packstuecken."""

    def __init__(self):
        # Wir gehen davon aus, dass folgende arrtibute von ausserhalb oder von abgeleiteten Klassen
        # definiert wird:
        self.fix = False  # the liefertermin is advisory or mandantory
        self.liefertermin = None
        self.itemlist = []

    @property
    def transportweg(self):
        """Returns the suggested method of shipping."""
        pass

    @property
    def transportzeit(self):
        """Returns the number of days this is likely to take to be shipped to the client."""
        pass

    @property
    def versandtermin(self):
        """Retuns the suggested date of shipping."""
        try:
            return self.liefertermin - self.transportzeit
        except TypeError:
            return self.liefertermin

    @property
    def anbruch(self):
        """Returns False if this Lieferung contains no items which need a export_package to be opened."""
        for item in self.itemlist:
            if item.anbruch:
                return True
        return False

    @property
    def volumen(self):
        """Returns the volume of all Items in this Lieferung in m^3."""
        return sum([x.volumen for x in self.itemlist])

    @property
    def gewicht(self):
        """Returns the gewicht of all Items in this Lieferung in g."""
        return sum([x.gewicht for x in self.itemlist])

    @property
    def max_packstueck_gewicht(self):
        """Returns the highest gewicht of any package in the shippment in g."""
        if self.itemlist:
            return max([x.max_packstueck_gewicht for x in self.itemlist])
        return 0

    @property
    def paletten(self):
        """Returns the number of pallets of all Items in this Lieferung."""
        return sum([x.paletten for x in self.itemlist])

    @property
    def versandpaletten(self):
        """Returns the number of pallets to be shipped. Always an Integer"""
        return math.ceil(self.paletten)

    @property
    def picks(self):
        """Returns the number of estimated picks for this Lieferung.

        A pick is defined as accessing a position in the warehouse."""
        return sum([x.picks for x in self.itemlist])

    @property
    def packstuecke(self):
        """Returns the number of "Greifeinheiten", meaning units to be taken out o the warehouse.
        This is an integer."""
        return sum([x.packstuecke for x in self.itemlist])

    @property
    def export_kartons(self):
        """Returns the estimated number of packages which will be shipped. This is a float."""
        return sum([x.export_kartons for x in self.itemlist])

    @property
    def export_karton_gewichte(self):
        """Returns the weights of the estimated number of packages which will be shipped in gramms."""
        ret = []
        for box in self.itemlist:
            ret.extend(box.export_karton_gewichte)
        return ret

    @property
    def kep(self):
        """Entscheidet, ob die Sendung mit einem Paketdienstleister verchickt werden kann."""
        if self.export_kartons > 10:
            return False
        if self.max_packstueck_gewicht > 31500:
            return False
        return True


class simpleTests(unittest.TestCase):
    """Very basic testing functionality."""

    def test_stupid(self):
        """Basic plausibility tests."""
        aitem = AbstractItem()
        aitem.menge = 12
        aitem.einzelgewicht = 3333
        aitem.palettenfaktor = 70
        aitem.produkte_pro_exportkarton = 2
        aitem.einzelvolumen = (750 * 200 * 100) / 10 / 10 / 10
        self.assertEqual(aitem.volumen, 180000)  # TODO: Unit? TOO BIG
        self.assertEqual(aitem.gewicht, 39996)
        self.assertEqual(aitem.anbruch, False)
        self.assertAlmostEqual(aitem.paletten, 0.171428571429)
        # print aitem.feinkommissionierung
        aitem2 = AbstractItem()
        aitem2.menge = 17
        aitem2.einzelgewicht = 9123
        aitem2.palettenfaktor = 30
        aitem2.produkte_pro_exportkarton = 5
        aitem2.einzelvolumen = (750 * 200 * 100) / 10 / 10 / 10

        alieferung = AbstractLieferung()
        alieferung.itemlist = [aitem]
        self.assertEqual(alieferung.volumen, 180000)  # TODO: Unit? TOO BIG
        self.assertEqual(alieferung.gewicht, 39996)
        self.assertEqual(alieferung.anbruch, False)
        self.assertAlmostEqual(alieferung.paletten, 0.171428571429)
        # print alieferung.fix
        # print alieferung.feinkommissionierung
        # print alieferung.transportzeit
        # print alieferung.versandtermin
        # print alieferung.liefertermin
        alieferung.itemlist = [aitem, aitem2]
        self.assertEqual(alieferung.volumen, 435000)
        self.assertEqual(alieferung.gewicht, 195087)
        self.assertAlmostEqual(alieferung.paletten, 0.738095238095)
        # print alieferung.transportweg
        # print alieferung.fix

if __name__ == '__main__':
    unittest.main()
