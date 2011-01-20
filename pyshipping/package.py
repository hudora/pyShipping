#!/usr/bin/env python
# encoding: utf-8
"""
package.py - shipping/cargo related calculations based on a unit of shipping (box, crate, package)

Created by Maximillian Dornseif on 2006-12-02.
Copyright HUDORA GmbH 2006, 2007, 2010
You might consider this BSD-Licensed.
"""

import doctest
import unittest


class Package(object):
    """Represents a package as used in cargo/shipping aplications."""

    def __init__(self, size, weight=0, nosort=False):
        """Generates a new Package object.

        The size can be given as an list of integers or an string where the sizes are determined by the letter 'x':
        >>> Package((300, 400, 500))
        <Package 500x400x300>
        >>> Package('300x400x500')
        <Package 500x400x300>
        """
        self.weight = weight
        if "x" in size:
            self.heigth, self.width, self.length = [int(x) for x in size.split('x')]
        else:
            self.heigth, self.width, self.length = size
        if not nosort:
            (self.heigth, self.width, self.length) = sorted((int(self.heigth), int(self.width),
                                                             int(self.length)), reverse=True)
        self.volume = self.heigth * self.width * self.length
        self.size = (self.heigth, self.width, self.length)

    def _get_gurtmass(self):
        """'gurtamss' is the circumference of the box plus the length - which is often used to
            calculate shipping costs.

            >>> Package((100,110,120)).gurtmass
            540
        """

        dimensions = (self.heigth, self.width, self.length)
        maxdimension = max(dimensions)
        otherdimensions = list(dimensions)
        del otherdimensions[otherdimensions.index(maxdimension)]
        return maxdimension + 2 * (sum(otherdimensions))
    gurtmass = property(_get_gurtmass)

    def hat_gleiche_seiten(self, other):
        """Prüft, ob other mindestens eine gleich grosse Seite mit self hat."""

        meineseiten = set([(self.heigth, self.width), (self.heigth, self.length), (self.width, self.length)])
        otherseiten = set([(other.heigth, other.width), (other.heigth, other.length),
                           (other.width, other.length)])
        return bool(meineseiten.intersection(otherseiten))

    def __getitem__(self, key):
        """The coordinates can be accessed as if the object is a tuple.
        >>> p = Package((500, 400, 300))
        >>> p[0]
        500
        """
        if key == 0:
            return self.heigth
        if key == 1:
            return self.width
        if key == 2:
            return self.length
        if isinstance(key, tuple):
            return (self.heigth, self.width, self.length)[key[0]:key[1]]
        if isinstance(key, slice):
            return (self.heigth, self.width, self.length)[key]
        raise IndexError

    def __contains__(self, other):
        """Checks if on package fits within an other.

        >>> Package((1600, 250, 480)) in Package((1600, 250, 480))
        True
        >>> Package((1600, 252, 480)) in Package((1600, 250, 480))
        False
        """
        return self[0] >= other[0] and self[1] >= other[1] and self[2] >= other[2]

    def __hash__(self):
        return self.heigth + (self.width << 16) + (self.length << 32)

    def __eq__(self, other):
        """Package objects are equal if they have exactly the same dimensions.

           Permutations of the dimensions are considered equal:

           >>> Package((100,110,120)) == Package((100,110,120))
           True
           >>> Package((120,110,100)) == Package((100,110,120))
           True
        """
        return (self.heigth == other.heigth and self.width == other.width and self.length == other.length)

    def __cmp__(self, other):
        """Enables to sort by Volume."""
        return cmp(self.volume, other.volume)

    def __mul__(self, multiplicand):
        """Package can be multiplied with an integer. This results in the Package beeing
           stacked along the biggest side.

           >>> Package((400,300,600)) * 2
           <Package 600x600x400>
           """
        return Package((self.heigth, self.width, self.length * multiplicand), self.weight * multiplicand)

    def __add__(self, other):
        """
            >>> Package((1600, 250, 480)) + Package((1600, 470, 480))
            <Package 1600x720x480>
            >>> Package((1600, 250, 480)) + Package((1600, 480, 480))
            <Package 1600x730x480>
            >>> Package((1600, 250, 480)) + Package((1600, 490, 480))
            <Package 1600x740x480>
            """
        meineseiten = set([(self.heigth, self.width), (self.heigth, self.length),
                           (self.width, self.length)])
        otherseiten = set([(other.heigth, other.width), (other.heigth, other.length),
                           (other.width, other.length)])
        if not meineseiten.intersection(otherseiten):
            raise ValueError("%s has no fitting sites to %s" % (self, other))
        candidates = sorted(meineseiten.intersection(otherseiten), reverse=True)
        stack_on = candidates[0]
        mysides = [self.heigth, self.width, self.length]
        mysides.remove(stack_on[0])
        mysides.remove(stack_on[1])
        othersides = [other.heigth, other.width, other.length]
        othersides.remove(stack_on[0])
        othersides.remove(stack_on[1])
        return Package((stack_on[0], stack_on[1], mysides[0] + othersides[0]), self.weight + other.weight)

    def __str__(self):
        if self.weight:
            return "%dx%dx%d %dg" % (self.heigth, self.width, self.length, self.weight)
        else:
            return "%dx%dx%d" % (self.heigth, self.width, self.length)

    def __repr__(self):
        if self.weight:
            return "<Package %dx%dx%d %d>" % (self.heigth, self.width, self.length, self.weight)
        else:
            return "<Package %dx%dx%d>" % (self.heigth, self.width, self.length)


def buendelung(kartons, maxweight=31000, maxgurtmass=3000):
    """Versucht Pakete so zu bündeln, so dass das Gurtmass nicht überschritten wird.

    Gibt die gebündelten Pakete und die nicht bündelbaren Pakete zurück.

    >>> buendelung([Package((800, 310, 250)), Package((800, 310, 250)), Package((800, 310, 250)), Package((800, 310, 250))])
    (1, [<Package 800x750x310>], [<Package 800x310x250>])
    >>> buendelung([Package((800, 310, 250)), Package((800, 310, 250)), Package((800, 310, 250)), Package((800, 310, 250)), Package((450, 290, 250)), Package((450, 290, 250))])
    (2, [<Package 800x750x310>, <Package 500x450x290>], [<Package 800x310x250>])
    """

    MAXKARTOONSIMBUENDEL = 6
    if not kartons:
        return 0, [], kartons
    gebuendelt = []
    rest = []
    lastkarton = kartons.pop(0)
    buendel = False
    buendelcounter = 0
    kartons_im_buendel = 1
    while kartons:
        currentcarton = kartons.pop(0)
        # check if 2 dimensions fit
        if (currentcarton.hat_gleiche_seiten(lastkarton)
            and (lastkarton.weight + currentcarton.weight < maxweight)
            and ((lastkarton + currentcarton).gurtmass < maxgurtmass)
            and (kartons_im_buendel < MAXKARTOONSIMBUENDEL)):
            # new carton has the same size in two dimensions and the sum of both in the third
            # ok, we can bundle
            lastkarton = (lastkarton + currentcarton)
            kartons_im_buendel += 1
            if buendel is False:
                # neues Bündel
                buendelcounter += 1
            buendel = True
        else:
            # different sizes, or too big
            if buendel:
                gebuendelt.append(lastkarton)
            else:
                rest.append(lastkarton)
            kartons_im_buendel = 1
            lastkarton = currentcarton
            buendel = False
    if buendel:
        gebuendelt.append(lastkarton)
    else:
        rest.append(lastkarton)
    return buendelcounter, gebuendelt, rest


def pack_in_bins(kartons, versandkarton):
    """Implements Bin-Packing.

    You provide it with a bin size and a list of Package Objects to be bined. Returns a list of lists
    representing the bins with the binned Packages and a list of Packages too big for binning.

    >>> pack_in_bins([Package('135x200x250'), Package('170x380x390'), Package('485x280x590'), Package('254x171x368'), Package('201x172x349'), Package('254x171x368')], \
                     Package('600x400x400'))
    ([[<Package 250x200x135>, <Package 349x201x172>, <Package 368x254x171>], [<Package 368x254x171>, <Package 390x380x170>]], [<Package 590x485x280>])
    """

    import pyshipping.binpack
    toobig, packagelist, bins, rest = [], [], [], []
    for box in sorted(kartons, reverse=True):
        if box not in versandkarton:
            # passt eh nicht
            toobig.append(box)
        else:
            packagelist.append(box)
    if packagelist:
        bins, rest = pyshipping.binpack.binpack(packagelist, versandkarton)
    return bins, toobig + rest


### Tests
class PackageTests(unittest.TestCase):
    """Simple tests for Package objects."""

    def test_init(self):
        """Tests object initialisation with different constructors."""
        self.assertEqual(Package((100, 100, 200)), Package(('100', '200', '100')))
        self.assertEqual(Package((100.0, 200.0, 200.0)), Package('200x200x100'))

    def test_eq(self):
        """Tests __eq__() implementation."""
        self.assertEqual(Package((200, 100, 200)), Package(('200', '100', '200')))
        self.assertNotEqual(Package((200, 200, 100)), Package(('100', '100', '200')))

    def test_volume(self):
        """Tests volume calculation"""
        self.assertEqual(4000000, Package((100, 200, 200)).volume)
        self.assertEqual(8000, Package((20, 20, 20)).volume)

    def test_str(self):
        """Test __unicode__ implementation."""
        self.assertEqual('200x200x100', Package((100, 200, 200)).__str__())
        self.assertEqual('200x200x100', Package('100x200x200').__str__())

    def test_repr(self):
        """Test __repr__ implementation."""
        self.assertEqual('<Package 200x200x100 44>', Package((100, 200, 200), 44).__repr__())

    def test_gurtmass(self):
        """Test gurtmass calculation."""
        self.assertEqual(800, Package((100, 200, 200)).gurtmass)
        self.assertEqual(900, Package((100, 200, 300)).gurtmass)
        self.assertEqual(1000, Package((200, 200, 200)).gurtmass)
        self.assertEqual(3060, Package((1600, 250, 480)).gurtmass)

    def test_mul(self):
        """Test multiplication."""
        self.assertEqual(Package((200, 200, 200)), Package((100, 200, 200)) * 2)

    def test_sort(self):
        """Test multiplication."""
        data = [Package((1600, 490, 480)), Package((1600, 470, 480)), Package((1600, 480, 480))]
        data.sort()
        self.assertEqual(data,
                         [Package((1600, 470, 480)), Package((1600, 480, 480)),
                          Package((1600, 490, 480))])


if __name__ == '__main__':

    factor = 0
    while True:
        factor += 1
        single = Package((750, 240, 220), 7400)
        multi = single * factor
        if multi.weight > 31000 or multi.gurtmass > 3000:
            multi = single * (factor - 1)
            #print factor - 1, multi, multi.gurtmass
            break

    doctest.testmod()
    unittest.main()
