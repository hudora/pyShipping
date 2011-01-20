#!/usr/bin/env python
# encoding: utf-8
"""
binpack.py

Created by Maximillian Dornseif on 2010-08-16.
Copyright (c) 2010 HUDORA. All rights reserved.
"""


import binpack_simple


def binpack(packages, bin=None, iterlimit=5000):
    return binpack_simple.binpack(packages, bin, iterlimit)


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
    print vorher, nachher, float(nachher) / vorher * 100


if __name__ == '__main__':
    print "py",
    test(binpack)


import time
from pyshipping.package import Package
