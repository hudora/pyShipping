#!/usr/bin/env python
# encoding: utf-8
"""
binpack.py

Created by Maximillian Dornseif on 2010-08-16.
Copyright (c) 2010 HUDORA. All rights reserved.
"""

import binpack_3dbpp
import binpack_simple


def binpack_alt(packages, bin=None):
    """
    This function contains linked in code (c) Copyright 1998, 2003, 2005, 2006 by
    
        David Pisinger                        Silvano Martello, Daniele Vigo
        DIKU, University of Copenhagen        DEIS, University of Bologna
        Universitetsparken 1                  Viale Risorgimento 2
        Copenhagen, Denmark                   Bologna, Italy
    
    This code can be used free of charge for research and academic purposes.
    See http://www.diku.dk/hjemmesider/ansatte/pisinger/new3dbpp/3dbpp.c
    """
    if not bin:
        bin = Package("600x400x400")
    boxcount, retboxes, stats = binpack_3dbpp.binpack(bin.size, [x.size for x in packages])
    return [bin] * boxcount, []


def binpack(packages, bin=None, iterlimit=5000):
    return binpack_simple.binpack(packages, bin, iterlimit)

import time
from pyshipping.package import Package


def test(func):
    fd = open('testdata.txt')
    vorher = 0
    nachher = 0
    start = time.time()
    counter = 0
    for line in fd:
        counter += 1
        if counter > 450:
            break
        packages = [Package(pack) for pack in line.strip().split()]
        if not packages:
            continue
        bins, rest = func(packages)
        if rest:
            print "invalid data", rest, line
        else:
            vorher += len(packages)
            nachher += len(bins)
    print time.time() - start,
    print vorher, nachher, float(nachher)/vorher*100

print "py", 
test(binpack)
print "c ", 
test(binpack_alt)

