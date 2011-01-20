#!/usr/bin/env python
# encoding: utf-8
"""
binpack_simple.py

This code implemnts 3D bin packing in pure Python

Bin packing in this context is calculating the best way to store a number of differently sized boxes in a
number of fixed sized "bins". It is what usually happens in a Warehouse bevore shipping.

The Algorithm has a simple fit first approach, but can archive relative good results because it tries
different rectangular rotations of the packages. Since the Algorithm can't interate over all possible
combinations we use a heuristic approach.

For a few dozen packages it reaches adaequate runtime. Below are the results calculated about a set of
500 real world packing problems.

Binsize     Runtime                 Recuction in shipped Packages
600x400x400 31.5993559361 4970 2033 40.9054325956
600x445x400 31.5596890450 4970 1854 37.3038229376
600x500x400 29.1432909966 4970 1685 33.9034205231


On the datasets we operate on we can archive comparable preformance to academic higly optimized C code
like David Pisinger's 3bpp:

     Runtime                 Recuction in shipped Packages
py   11.3468761444 2721 1066 39.1767732451
3bpp 9.95857691765 2721 1086 39.9117971334

The Python implementation is somewhat slower but can archive slightly better packing results on our
datasets.


Created by Maximillian Dornseif on 2010-08-14.
Copyright (c) 2010 HUDORA. All rights reserved.
"""


import time
import random


def packstrip(bin, p):
    """Creates a Strip which fits into bin.

    Returns the Packages to be used in the strip, the dimensions of the strip as a 3-tuple
    and a list of "left over" packages.
    """
    # This code is somewhat optimized and somewhat unreadable
    s = []                # strip
    r = []                # rest
    ss = sw = sl = 0      # stripsize
    bs = bin.heigth       # binsize
    sapp = s.append       # speedup
    rapp = r.append       # speedup
    ppop = p.pop          # speedup
    while p and (ss <= bs):
        n = ppop(0)
        nh, nw, nl = n.size
        if ss + nh <= bs:
            ss += nh
            sapp(n)
            if nw > sw:
                sw = nw
            if nl > sl:
                sl = nl
        else:
            rapp(n)
    return s, (ss, sw, sl), r + p


def packlayer(bin, packages):
    strips = []
    layersize = 0
    layerx = 0
    layery = 0
    binsize = bin.width
    while packages:
        strip, (sizex, stripsize, sizez), rest = packstrip(bin, packages)
        if layersize + stripsize <= binsize:
            if not strip:
                # we were not able to pack anything
                break
            layersize += stripsize
            layerx = max([sizex, layerx])
            layery = max([sizez, layery])
            strips.extend(strip)
            packages = rest
        else:
            # Next Layer please
            packages = strip + rest
            break
    return strips, (layerx, layersize, layery), packages


def packbin(bin, packages):
    packages.sort()
    layers = []
    contentheigth = 0
    contentx = 0
    contenty = 0
    binsize = bin.length
    while packages:
        layer, (sizex, sizey, layersize), rest = packlayer(bin, packages)
        if contentheigth + layersize <= binsize:
            if not layer:
                # we were not able to pack anything
                break
            contentheigth += layersize
            contentx = max([contentx, sizex])
            contenty = max([contenty, sizey])
            layers.extend(layer)
            packages = rest
        else:
            # Next Bin please
            packages = layer + rest
            break
    return layers, (contentx, contenty, contentheigth), packages


def packit(bin, originalpackages):
    packedbins = []
    packages = sorted(originalpackages)
    while packages:
        packagesinbin, (binx, biny, binz), rest = packbin(bin, packages)
        if not packagesinbin:
            # we were not able to pack anything
            break
        packedbins.append(packagesinbin)
        packages = rest
    # we now have a result, try to get a better result by rotating some bins

    return packedbins, rest


# In newer Python versions these van be imported:
# from itertools import permutations
def product(*args, **kwds):
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = map(tuple, args) * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x + [y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)


def permutations(iterable, r=None):
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    for indices in product(range(n), repeat=r):
        if len(set(indices)) == r:
            yield tuple(pool[i] for i in indices)


class Timeout(Exception):
    pass


def allpermutations_helper(permuted, todo, maxcounter, callback, bin, bestpack, counter):
    if not todo:
        return counter + callback(bin, permuted, bestpack)
    else:
        others = todo[1:]
        thispackage = todo[0]
        for dimensions in set(permutations((thispackage[0], thispackage[1], thispackage[2]))):
            thispackage = Package(dimensions, nosort=True)
            if thispackage in bin:
                counter = allpermutations_helper(permuted + [thispackage], others, maxcounter, callback,
                                                 bin, bestpack, counter)
            if counter > maxcounter:
                raise Timeout('more than %d iterations tries' % counter)
        return counter


def trypack(bin, packages, bestpack):
    bins, rest = packit(bin, packages)
    if len(bins) < bestpack['bincount']:
        bestpack['bincount'] = len(bins)
        bestpack['bins'] = bins
        bestpack['rest'] = rest
    if bestpack['bincount'] < 2:
        raise Timeout('optimal solution found')
    return len(packages)


def allpermutations(todo, bin, iterlimit=5000):
    random.seed(1)
    random.shuffle(todo)
    bestpack = dict(bincount=len(todo) + 1)
    try:
        # First try unpermuted
        trypack(bin, todo, bestpack)
        # now try permutations
        allpermutations_helper([], todo, iterlimit, trypack, bin, bestpack, 0)
    except Timeout:
        pass
    return bestpack['bins'], bestpack['rest']


def binpack(packages, bin=None, iterlimit=5000):
    """Packs a list of Package() objects into a number of equal-sized bins.

    Returns a list of bins listing the packages within the bins and a list of packages which can't be
    packed because they are to big."""
    if not bin:
        bin = Package("600x400x400")
    return allpermutations(packages, bin, iterlimit)


def test():
    fd = open('testdata.txt')
    vorher = 0
    nachher = 0
    start = time.time()
    for line in fd:
        packages = [Package(pack) for pack in line.strip().split()]
        if not packages:
            continue
        bins, rest = binpack(packages)
        if rest:
            print "invalid data", rest, line
        else:
            vorher += len(packages)
            nachher += len(bins)
    print time.time() - start,
    print vorher, nachher, float(nachher) / vorher * 100


if __name__ == '__main__':
    import cProfile
    cProfile.run('test()')


from pyshipping.package import Package
