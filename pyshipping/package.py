#!/usr/bin/env python
# encoding: utf-8
"""
package.py - shipping/cargo related calculations based on a unit of shipping (box, crate, package)

Created by Maximillian Dornseif on 2006-12-02.
Copyrigt HUDORA GmbH 2006, 2007
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
        <PackageSize 300x400x500>
        >>> PackageSize('300x400x500')
        <PackageSize 300x400x500>
        """
        if "x" in size:
            self.heigth, self.width, self.length = size.split('x')
        else:
            self.heigth, self.width, self.length = size
        self.heigth, self.width, self.length = int(self.heigth), int(self.width), int(self.length)
    
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
        """'gurtamss' is the circumference of the girth plus the length - which is often used to
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
    
    def __eq__(self, other):
        """PackageSize objects are equal if they have exactly the same dimensions.
           
           Permutations of the dimensions are not considered equal:
           
           >>> PackageSize((100,110,120)) == PackageSize((100,110,120))
           True
           >>> PackageSize((120,110,100)) == PackageSize((100,110,120))
           False
       """
        
        return (self.heigth == other.heigth and self.width == other.width and self.length == other.length)
    
    def __mul__(self, multiplicand):
        """PackageSize can be multiplied with an integer. This results in the PackageSize beeing
           stacked along the biggest side.
           
           >>> PackageSize((400,300,600)) * 2
           <PackageSize 400x600x600>
           """
        dimensions = [self.heigth, self.width, self.length]
        mindimension = min(dimensions)
        if mindimension == self.heigth:
            return PackageSize((self.heigth*multiplicand, self.width, self.length))
        elif mindimension == self.width:
            return PackageSize((self.heigth, self.width*multiplicand, self.length))
        elif mindimension == self.length:
            return PackageSize((self.heigth, self.width, self.length*multiplicand))
    
    def __str__(self):
        return "%dx%dx%d" % (self.heigth, self.width, self.length)
    
    def __repr__(self):
        return "<PackageSize %dx%dx%d>" % (self.heigth, self.width, self.length)
    

class Package:
    """Represents a package as used in cargo/shipping aplications."""
    
    def __init__(self, size=None, weight=None):
        """Creates a packstueck object.
        
        Size can be the 3 dimensions of a package in mm. Note that we only support box-shaped packages. Size
        may be given as a tuple of integers or a string in th eformat '111x222x333'. See PackageSize.__init__
        for further details."""
        
        self.size = size
        self.weight = weight
        
        if size:
            self.size = PackageSize(size)
            
    def __mul__(self, multiplicand):
        return Package(str(self.size*multiplicand), self.weight*multiplicand)
    
    def __str__(self):
        ret = ['Package']
        if self.size:
            ret.append(unicode(self.size))
        if self.weight:
            ret.append(unicode(self.weight))
        return ', '.join(ret)


### Tests

class PackageSizeTests(unittest.TestCase):
    """Simple tests for PackageSize objects."""
    
    def test_init(self):
        """Tests object initialisation with different constructors."""
        self.assertEqual(PackageSize((100, 200, 200)), PackageSize(('100', '200', '200')))
        self.assertEqual(PackageSize((100.0, 200.0, 200.0)), PackageSize('100x200x200'))
    
    def test_eq(self):
        """Tests __eq__() implementation."""
        self.assertEqual(PackageSize((200, 100, 200)), PackageSize(('200', '100', '200')))
        self.assertNotEqual(PackageSize((200, 200, 100)), PackageSize(('200', '100', '200')))
        
    def test_volume(self):
        """Tests volume calculation"""
        self.assertEqual(4000000, PackageSize((100, 200, 200)).volume)
        self.assertEqual(8000, PackageSize((20, 20, 20)).volume)
    
    def test_str(self):
        """Test __unicode__ implementation."""
        self.assertEqual('100x200x200', PackageSize((100, 200, 200)).__str__())
        self.assertEqual('100x200x200', PackageSize('100x200x200').__str__())
    
    def test_repr(self):
        """Test __repr__ implementation."""
        self.assertEqual('<PackageSize 100x200x200>', PackageSize((100, 200, 200)).__repr__())
    
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
        if multi.weight > 31000 or multi.size.gurtmass > 3000:
            multi = single * (factor - 1)
            print factor - 1, multi, multi.size.gurtmass
            break
            
            
    doctest.testmod()
    unittest.main()
