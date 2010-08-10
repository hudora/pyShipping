#!/usr/bin/env python
# encoding: utf-8
"""
package.py - shipping/cargo related calculations based on a unit of shipping (box, crate, package)

Created by Maximillian Dornseif on 2006-12-02.
Copyrigt HUDORA GmbH 2006, 2007, 2010
You might consider this BSD-Licensed.
"""

import doctest
import unittest


class PackageSize(object):
    """PackageSize objects capture the spartial properties of a Package."""
    
    def __init__(self, size):
        """Generates a new PackageSize object.
        
        The size can be given as an list of integers or an string where the sizes are determined by the letter 'x':
        >>> PackageSize((300, 400, 500))
        <PackageSize 500x400x300>
        >>> PackageSize('300x400x500')
        <PackageSize 500x400x300>
        """
        if "x" in size:
            self.heigth, self.width, self.length = size.split('x')
        else:
            self.heigth, self.width, self.length = size
        (self.heigth, self.width, self.length) = sorted((int(self.heigth), int(self.width),
                                                         int(self.length)), reverse=True)

    def __getitem__(self, key):
        """The coordinates can be accessed as if the object is a tuple. 
        >>> p = PackageSize((500, 400, 300))
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

    def _get_volume(self):
        """Calculates the volume of a PackageSize object.
            
            Since the volume is calculated in mm^3 very large numbers occur. Divide by 1000 to get cm^3
            or by 1 000 000 000 to get m^3.
            
           >>> PackageSize((100,110,120)).volume
           1320000
        """
        return self.heigth * self.width * self.length
    volume = property(_get_volume)
    
    def _get_gurtmass(self):
        """'gurtamss' is the circumference of the box plus the length - which is often used to
            calculate shipping costs.
            
            >>> PackageSize((100,110,120)).gurtmass
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
        
        meineseiten = set([(self.heigth, self.width), (self.heigth, self.length),(self.heigth, self.length)])
        otherseiten = set([(other.heigth, other.width), (other.heigth, other.length),(other.heigth, other.length)])
        return not meineseiten.isdisjoint(otherseiten)

    def __eq__(self, other):
        """PackageSize objects are equal if they have exactly the same dimensions.
           
           Permutations of the dimensions are considered equal:
           
           >>> PackageSize((100,110,120)) == PackageSize((100,110,120))
           True
           >>> PackageSize((120,110,100)) == PackageSize((100,110,120))
           True
       """
        
        return (self.heigth == other.heigth and self.width == other.width and self.length == other.length)
    
    def __mul__(self, multiplicand):
        """PackageSize can be multiplied with an integer. This results in the PackageSize beeing
           stacked along the biggest side.
           
           >>> PackageSize((400,300,600)) * 2
           <PackageSize 600x600x400>
           """

        return PackageSize((self.heigth, self.width, self.length*multiplicand))

    def __add__(self, other):
        """
            >>> PackageSize((1600, 250, 480)) + PackageSize((1600, 470, 480))
            <PackageSize 1600x720x480>
            >>> PackageSize((1600, 250, 480)) + PackageSize((1600, 480, 480))
            <PackageSize 1600x730x480>
            >>> PackageSize((1600, 250, 480)) + PackageSize((1600, 490, 480))
            <PackageSize 1600x740x480>
            """
        
        meineseiten = set([(self.heigth, self.width), (self.heigth, self.length),(self.heigth, self.length)])
        otherseiten = set([(other.heigth, other.width), (other.heigth, other.length),(other.heigth, other.length)])
        if meineseiten.isdisjoint(otherseiten):
            raise ValueError("%s has no fitting sites to %s" % (self, other))
        candidates = sorted(meineseiten.intersection(otherseiten), reverse=True)
        stack_on = candidates[0]
        mysides = [self.heigth, self.width, self.length]
        mysides.remove(stack_on[0])
        mysides.remove(stack_on[1])
        othersides = [other.heigth, other.width, other.length]
        othersides.remove(stack_on[0])
        othersides.remove(stack_on[1])
        return PackageSize((stack_on[0], stack_on[1], mysides[0] + othersides[0]))

    def __str__(self):
        return "%dx%dx%d" % (self.heigth, self.width, self.length)
    
    def __repr__(self):
        return "<PackageSize %dx%dx%d>" % (self.heigth, self.width, self.length)


class Package(PackageSize):
    """Represents a package as used in cargo/shipping aplications."""
    
    def __init__(self, size=None, weight=None):
        """Creates a packstueck object.
        
        Size can be the 3 dimensions of a package in mm. Note that we only support box-shaped packages. Size
        may be given as a tuple of integers or a string in th eformat '111x222x333'. See PackageSize.__init__
        for further details."""
        self.weight = weight
        PackageSize.__init__(self, size)

    def __mul__(self, multiplicand):
        return Package((self.heigth, self.width, self.length*multiplicand), self.weight*multiplicand)

    def __str__(self):
        return "<Package %dx%dx%d %d>" % (self.heigth, self.width, self.length, self.weight)


def buendelung(kartons, maxweight=32000, maxgurtmass=3000):
    """Versucht Pakete so zu bündeln, so dass das Gurtmass nicht überschritten wird.
    
    Gibt die gebündelten Pakete und die Zahl der benötigten Bündelungsvorgänge zurück.
    
    >>> buendelung([Package((800, 310, 250)), Package((800, 310, 250)), Package((800, 310, 250)), Package((800, 310, 250))])
    ([<PackageSize 800x560x500>, <PackageSize 800x310x250>], 1)
    >>> buendelung([Package((800, 310, 250)), Package((800, 310, 250)), Package((800, 310, 250)), Package((800, 310, 250)), Package((450, 290, 250)), Package((450, 290, 250))])
    ([<PackageSize 800x560x500>, <PackageSize 800x310x250>, <PackageSize 500x450x290>], 2)
    """
    
    if not kartons:
        return kartons
    ret = []
    lastkarton = kartons.pop(0)
    buendel = False
    buendelcounter = 0
    while kartons:
        currentcarton = kartons.pop(0)
        # check if 2 dimensions fit
        if currentcarton.hat_gleiche_seiten(lastkarton):
            # new carton has the same size in two dimensions and the sum of both in the third
            newcarton = Package(lastkarton[:2] + tuple([currentcarton[2] + lastkarton[2]]))
            # gurtmass pruefen
            if newcarton.gurtmass < maxgurtmass:
                # ok, we can bundle
                lastkarton = newcarton
                if buendel is False:
                    buendelcounter += 1
                buendel = True
            else:
                # too big
                ret.append(lastkarton)
                lastkarton = currentcarton
                buendel = False
        else:
            # different sizes, ditch for now
            ret.append(lastkarton)
            lastkarton = currentcarton
            buendel = False
    ret.append(lastkarton)
    return ret, buendelcounter



### Tests

class PackageSizeTests(unittest.TestCase):
    """Simple tests for PackageSize objects."""
    
    def test_init(self):
        """Tests object initialisation with different constructors."""
        self.assertEqual(PackageSize((100, 100, 200)), PackageSize(('100', '200', '100')))
        self.assertEqual(PackageSize((100.0, 200.0, 200.0)), PackageSize('200x200x100'))
    
    def test_eq(self):
        """Tests __eq__() implementation."""
        self.assertEqual(PackageSize((200, 100, 200)), PackageSize(('200', '100', '200')))
        self.assertNotEqual(PackageSize((200, 200, 100)), PackageSize(('100', '100', '200')))
        
    def test_volume(self):
        """Tests volume calculation"""
        self.assertEqual(4000000, PackageSize((100, 200, 200)).volume)
        self.assertEqual(8000, PackageSize((20, 20, 20)).volume)
    
    def test_str(self):
        """Test __unicode__ implementation."""
        self.assertEqual('200x200x100', PackageSize((100, 200, 200)).__str__())
        self.assertEqual('200x200x100', PackageSize('100x200x200').__str__())
    
    def test_repr(self):
        """Test __repr__ implementation."""
        self.assertEqual('<PackageSize 200x200x100>', PackageSize((100, 200, 200)).__repr__())
    
    def test_gurtmass(self):
        """Test gurtmass calculation."""
        self.assertEqual(800, PackageSize((100, 200, 200)).gurtmass)
        self.assertEqual(900, PackageSize((100, 200, 300)).gurtmass)
        self.assertEqual(1000, PackageSize((200, 200, 200)).gurtmass)
        self.assertEqual(3060, PackageSize((1600, 250, 480)).gurtmass)
    
    def test_mul(self):
        """Test multiplication."""
        self.assertEqual(PackageSize((200, 200, 200)), PackageSize((100, 200, 200))*2)
    

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
