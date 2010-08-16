# coding: utf-8
# 13.5036859512 4903 2018 41.1584744034
# 10.6387898922 4903 2018 41.1584744034
# 9.07241487503 4903 2018 41.1584744034
# 8.48105192184 4903 2018 41.1584744034

# 35.9507751465 4903 2007 40.9341219661
# 35.310297966  4903 2007 40.9341219661
# 34.8188328743 4903 2007 40.9341219661
# 33.2343409061 4903 2007 40.9341219661
# 33.9700279236 4903 2007 40.9341219661

# 33.4133989811 4970 2033 40.9054325956
# 33.1115708351 4970 2033 40.9054325956
# 33.8842139244 4970 2033 40.9054325956
# 32.5221009254 4970 2033 40.9054325956
# 33.1047270298 4970 2033 40.9054325956


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
            rest = strip + rest
            break
    return strips, (layerx, layersize, layery), rest + packages


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


import itertools
import random

class Timeout(Exception):
    pass


def allpermutations_helper(permuted, todo, maxcounter, callback, bin, bestpack, counter):
    if not todo:
        return counter + callback(bin, permuted, bestpack)
    else:
        others = todo[1:]
        thispackage = todo[0]
        for dimensions in set(itertools.permutations((thispackage[0], thispackage[1], thispackage[2]))):
            thispackage = Package(dimensions, nosort=True)
            if thispackage in bin:
                counter = allpermutations_helper(permuted+[thispackage], others, maxcounter, callback, bin,
                                                 bestpack, counter)
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


def allpermutations(todo):
    bin = Package("600x400x400")
    random.seed(1)
    random.shuffle(todo)
    bestpack = dict(bincount=len(todo)+1)
    try:
        # First try unpermuted
        trypack(bin, todo, bestpack)
        # now try permutations
        allpermutations_helper([], todo, 5000, trypack, bin, bestpack, 0)
    except Timeout:
        pass
    return bestpack['bins'], bestpack['rest']


from pyshipping.package import Package
import time


def test():
    fd = open('testdata.txt')
    vorher = 0
    nachher = 0
    start = time.time()
    for line in fd:
        packages = [Package(pack) for pack in line.strip().split()]
        if not packages:
            continue
        bins, rest = allpermutations(packages)
        if rest:
            print "invalid data", rest, line
        else:
            #print len(packages), len(bins)
            vorher += len(packages)
            nachher += len(bins)
    print time.time() - start,
    print vorher, nachher, float(nachher)/vorher*100

import cProfile
cProfile.run('test()')
