#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys

from multiprocessing import Process, Lock, Value

from random import shuffle
import math

import time

import collections
import copy
import itertools

# Best global score
bestScore = Value('i', -99999999999999999999)

# Tuple of (list, resultValue)
def printResult(lock, result, initiator, time):
    lock.acquire()
    global bestScore
    if result[1] > bestScore.value:
        bestScore.value = result[1]

        if False:
            print 'initiator: {:20}, score: {:7}, time: {:06.2f}, result: {}...'.format(initiator, bestScore.value, time, result[0])
        else:
            print result[0]
        sys.stdout.flush()

    lock.release()

def productFits(mask, product, xoffset, yoffset):

    for y in range(yoffset, yoffset+product[1]):
        for x in range(xoffset, xoffset+product[0]):
            if mask[y][x] != -1:
                return False
    return True

# Only check the outline and not all inside.
def productFitsFast(mask, product, xoffset, yoffset, bag):

    for y in range(yoffset, yoffset+product[1]):
        if y >= 0 and y < bag[1] and xoffset >= 0 and xoffset < bag[0]:
            if mask[y][xoffset] != -1:
                return False
        else:
            return False
    for y in range(yoffset, yoffset+product[1]):
        if y >= 0 and y < bag[1] and xoffset+product[0]-1 >= 0 and xoffset+product[0]-1 < bag[0]:
            if mask[y][xoffset+product[0]-1] != -1:
                return False
        else:
            return False

    for x in range(xoffset, xoffset+product[0]):
        if yoffset >= 0 and yoffset < bag[1] and x >= 0 and x < bag[0]:
            if mask[yoffset][x] != -1:
                return False
        else:
            return False
    for x in range(xoffset, xoffset+product[0]):
        if yoffset+product[1]-1 >= 0 and yoffset+product[1]-1 < bag[1] and x >= 0 and x < bag[0]:
            if mask[yoffset+product[1]-1][x] != -1:
                return False
        else:
            return False
    return True

def productToMask(mask, product, xoffset, yoffset):
    for y in range(yoffset, yoffset+product[1]):
        for x in range(xoffset, xoffset+product[0]):
            mask[y][x] = product[3]

def countFreeBlocks(mask, x1, y1, x2, y2):
    freeBlockCount = 0
    for y in range(y1, y2):
        for x in range(x1, x2):
            if mask[y][x] == -1:
                freeBlockCount += 1
    return freeBlockCount

def countSurroundingBlocks(mask, width, height, x, y, product):
    blockCount = 0
    if x == 0:
        blockCount += product[1]
    else:
        blockCount += countFreeBlocks(mask, x-1, y, x, y+product[1])

    if x+product[0] == width:
        blockCount += product[1]
    else:
        blockCount += countFreeBlocks(mask, x+product[0], y, x+product[0]+1, y+product[1])

    if y == 0:
        blockCount += product[0]
    else:
        blockCount += countFreeBlocks(mask, x, y-1, x+product[0], y)

    if y+product[1] == height:
        blockCount += product[0]
    else:
        blockCount += countFreeBlocks(mask, x, y+product[1], x+product[0], y+product[1]+1)

    return blockCount


# Try to get at most outer blocks aligned with other blocks or the side. So at least two sides are aligned to something!
def placeProductInBagIntelligent(mask, width, height, product):
    productPlaced = False
    countY = 0
    countX = 0
    # (x, y, surroundingBlockCount)
    bestPosition = (-1, -1, -1)
    bestScore = product[0] + product[1]

    for y in range(countY, height-product[1]+1):
        countX = 0
        for x in range(countX, width-product[0]+1):
            if productFits(mask, product, countX, countY):
                blockCount = countSurroundingBlocks(mask, width, height, countX, countY, product)
                if blockCount == bestScore:
                    bestPosition = (countX, countY, blockCount)
                    productPlaced = True
                    break
                if blockCount > bestPosition[2]:
                    bestPosition = (countX, countY, blockCount)

            countX += 1
        countY += 1
        if productPlaced:
            break

    if bestPosition[2] != -1:
        productToMask(mask, product, bestPosition[0], bestPosition[1])
        productPlaced = True

    return productPlaced

# Just take the first free space!
def placeProductInBagDumb(mask, width, height, product):
    countY = 0
    countX = 0

    for y in range(countY, height-product[1]+1):
        countX = 0
        for x in range(countX, width-product[0]+1):
            if productFits(mask, product, countX, countY):
                productToMask(mask, product, countX, countY)
                return True
            countX += 1

        countY += 1

    return False

def maskToList(mask, width, height, products, fillCosts):

    alreadyFound = [-1]
    resultList = []
    resultValue = 0

    for y in range(height):
        for x in range(width):

            if mask[y][x] == -1:
                resultValue -= fillCosts
                continue

            if not mask[y][x] in alreadyFound:
                alreadyFound.append(mask[y][x])
                resultList.append((x,y,mask[y][x]))
                resultValue += products[mask[y][x]][2]

    return resultList, resultValue


def createMask(bag):
    width, height = bag[0], bag[1]
    return [[-1 for x in range(width)] for y in range(height)]

def ppMask(mask, bag):
    for y in range(bag[1]):
        for x in range(bag[0]):
            print " %02d " % (mask[bag[1]-y-1][x]),
        print ""

def ppCCOAs(ccoaList):
    if not ccoaList:
        print "ccoaList is empty"
    for ccoa in ccoaList:
        print ccoa

def ppProducts(products):
    if not products:
        print "ccoaList is empty"
    for p in products:
        print p

# This function is allowed and required to delete elements of 'products'!
# Returns (list, resultValue)
def fillBag(algorithm, bag, products, savedProducts, fillCosts):

    mask = createMask(bag)

    listToDelete = []

    for i in range(len(products)):
        if algorithm(mask, bag[0], bag[1], products[i]):
            listToDelete.append(i)

    listToDelete = sorted(listToDelete)
    offset = 0

    for index in listToDelete:
        del products[index - offset]
        offset += 1

    return maskToList(mask, bag[0], bag[1], savedProducts, fillCosts)


def calcGreedyFilling(lock, algorithm, bags, products, fillCosts, initiator, verbose, start):

    resultList = [[] for x in range(len(bags))]
    resultValue = 0

    savedProducts = sorted(list(products), key=lambda x: x[3])

    for bIndex in range(len(bags)):
        bag = bags[bIndex]
        res, value = fillBag(algorithm, bag, products, savedProducts, fillCosts)
        #print value
        # put the calculated bag to the right position (just like they came in originally!)
        resultList[bag[2]] = res
        resultValue += value
        if verbose:
            restValue = reduce(lambda x,y: x - y[0]*y[1]*fillCosts, bags[bIndex+1:], 0)
            printResult(lock, (resultList, resultValue+restValue), initiator, time.time()-start)

    printResult(lock, (resultList, resultValue), initiator, time.time()-start)


########################################################################
#### A two-level search algorithm for 2D rectangular packing problem ###
########################################################################

CCOA    = collections.namedtuple('CCOA', 'unitIndex pos cornerType pIndex degree')
Corner  = collections.namedtuple('Corner', 'unitIndex pos cornerType')
Product = collections.namedtuple('Product', 'width height value pIndex isPlaced')
Unit    = collections.namedtuple('Unit', 'bag mask placedProducts')

# Distance between two points
def d(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# Generates all 4 corner points for a given rectangle.
# p == (width, height)
def rectanglePoints(x, y, p):
    return [(x,y), (x+p[0],y), (x+p[0],y+p[1]), (x,y+p[1])]

# Calculates the minimum distance between two relevant products.
# x, y is the corner where p is to be placed. pr2 is already placed.
# pr2 == (x, y, width, height, value, index)
def minDistance(x, y, p, cornerType, pr2):
    # p lays between pr2 on the y axis or pr2 lays between p.
    if (pr2[1] <= y <= pr2[1]+pr2[3]) or (pr2[1] <= y+p[1] <= pr2[1]+pr2[3]) or (y <= pr2[1] <= y+p[1]) or (y <= pr2[1]+pr2[3] <= y+p[1]):
        if cornerType[0] > 0:
            return pr2[0] - (x+p[0])
        else:
            return x - (pr2[0]+pr2[2])

    if (pr2[0] <= x <= pr2[0]+pr2[2]) or (pr2[0] <= x+p[0] <= pr2[0]+pr2[2]) or (x <= pr2[0] <= x+p[0]) or (x <= pr2[0]+pr2[2] <= x+p[0]):
        if cornerType[1] > 0:
            return pr2[1] - (y+p[1])
        else:
            return y - (pr2[1]+pr2[3])

    # Now only the distance between two cornerPoints has to be considered
    checkX  = x+p[0] if cornerType[0] > 0 else x
    checkY  = y+p[1] if cornerType[1] > 0 else y

    checkX2 = pr2[0] if cornerType[0] > 0 else pr2[0]+pr2[2]
    checkY2 = pr2[1] if cornerType[1] > 0 else pr2[1]+pr2[3]

    return d((checkX, checkY), (checkX2, checkY2))

# Minimum distance to the two relevant sides of the bag.
def minDistanceToSides(x, y, cornerType, product, bag):
    xDiff = x-product[0]
    yDiff = y-product[1]+1

    if cornerType[0] > 0:
        xDiff = bag[0] - (x+product[0])
    if cornerType[1] > 0:
        yDiff = bag[1] - (y+product[1])

    return min(xDiff, yDiff)

# calculates if the product is relevant to the product to be placed
# It placedProduct is 'behind' product, there is no sense in calculating a distance.
def productInRange(x, y, cornerType, product, placedProduct):

    points = rectanglePoints(placedProduct[0], placedProduct[1], (placedProduct[2],placedProduct[3]))
    inRange = True

    if cornerType[0] > 0:
        inRange = inRange and reduce(lambda a,b: a or b[0] > x, points, False)
    else:
        inRange = inRange and reduce(lambda a,b: a or b[0] < x+product[0], points, False)

    if cornerType[1] > 0:
        inRange = inRange and reduce(lambda a,b: a or b[1] > y, points, False)
    else:
        inRange = inRange and reduce(lambda a,b: a or b[1] < y+product[1], points, False)

    return inRange

# The minimum distance to all relevant placed products!
def minDistanceToProducts(x, y, cornerType, product, placedProducts, bag):
    minDist = 1000000000

    for p in placedProducts:
        # filter all products that cannot be important (out of range)!
        if productInRange(x, y, cornerType, product, p):
            dist = minDistance(x, y, product, cornerType, p)
            if dist == 0:
                return 0
            minDist = min(minDist, dist)
    return minDist

# placedProducts == [(x, y, width, height, value, index), ...]
# placedProducts == All already in C at (x,y) placed products.
# cornerType == (dx,dy) in range [-1|1]
#   (-1,1) == bottom right corner.
def calcDegree(x,y,cornerType,product, placedProducts, bag):

    # Calc distance to two bag sides
    minDistSide = minDistanceToSides(x, y, cornerType, product, bag)
    minDistProd = minDistanceToProducts(x, y, cornerType, product, placedProducts, bag)
    globalMin   = min(minDistSide, minDistProd)
    return 1.0 - globalMin / ((product[0]+product[1])/2.0)


def recalculateDegrees(ccoaList, products, units):
    bestCCOA = None
    for i in range(len(ccoaList)):
        ccoa = ccoaList[i]
        placedProducts = units[ccoa.unitIndex].placedProducts
        bag = units[ccoa.unitIndex].bag
        dg = calcDegree(ccoa.pos[0], ccoa.pos[1], ccoa.cornerType, products[ccoa.pIndex], placedProducts, bag)
        newCCOA = CCOA(unitIndex=ccoa.unitIndex, pos=ccoa.pos, cornerType=ccoa.cornerType, pIndex=ccoa.pIndex, degree=dg)
        ccoaList[i] = newCCOA

        #if not bestCCOA or newCCOA.degree > bestCCOA.degree:
        #    bestCCOA = newCCOA

        if not bestCCOA:
            bestCCOA = newCCOA
            continue

        degreeDiff = math.fabs(newCCOA.degree - bestCCOA.degree)

        # The attempt to value value and degree together...
        if degreeDiff < 0.0001:
            if products[newCCOA.pIndex].value > products[bestCCOA.pIndex].value:
                bestCCOA = newCCOA
        else:
            if newCCOA.degree > bestCCOA.degree:
                bestCCOA = newCCOA

        del ccoa
    return bestCCOA


# Check inside the mask if the product does not overlap with some other product.
# Then create a CCOA.
def createCCOA(corner, product, units):

    # Iterate the outline of the product on the mask on the corner-position.
    # If it hits something, return None. Otherwise create a SSOA.

    placeX = corner.pos[0] if corner.cornerType[0] > 0 else corner.pos[0]-product[0]+1
    placeY = corner.pos[1] if corner.cornerType[1] > 0 else corner.pos[1]-product[1]+1

    if productFitsFast(units[corner.unitIndex].mask, product, placeX, placeY, units[corner.unitIndex].bag):
        pDegree = calcDegree(corner.pos[0], corner.pos[1], corner.cornerType, product, units[corner.unitIndex].placedProducts, units[corner.unitIndex].bag)
        return CCOA(unitIndex=corner.unitIndex, pos=corner.pos, cornerType=corner.cornerType, pIndex=product[3], degree=pDegree)
    else:
        return None

def removeAllInvalidCCOAs(ccoas, placedccoa, products, units):
    toDelete = []
    for i in range(len(ccoas)):
        ccoa = ccoas[i]
        if ccoa.pos == placedccoa.pos or ccoa.pIndex == placedccoa.pIndex:
            toDelete.append(i)
            continue

        placeX = ccoa.pos[0] if ccoa.cornerType[0] > 0 else ccoa.pos[0]-products[ccoa.pIndex][0]+1
        placeY = ccoa.pos[1] if ccoa.cornerType[1] > 0 else ccoa.pos[1]-products[ccoa.pIndex][1]+1

        if not productFitsFast(units[ccoa.unitIndex].mask, products[ccoa.pIndex], placeX, placeY, units[ccoa.unitIndex].bag):
            toDelete.append(i)

    toDelete = sorted(toDelete, reverse=True)
    for i in toDelete:
        del ccoas[i]

def countNeighbours(bag, mask, x, y):
    count = 0
    corner = [1,1]

    # Sides
    if x == 0:
        count += 1
        corner[0] = 1
    if x == bag[0]-1:
        count += 1
        corner[0] = -1
    if y == 0:
        count += 1
        corner[1] = 1
    if y == bag[1]-1:
        count += 1
        corner[1] = -1

    # Other products
    if x >= 1 and mask[y][x-1] != -1:
        count += 1
        corner[0] = 1
    if x < (bag[0]-1) and mask[y][x+1] != -1:
        count += 1
        corner[0] = -1
    if y >= 1 and mask[y-1][x] != -1:
        count += 1
        corner[1] = 1
    if y < (bag[1]-1) and mask[y+1][x] != -1:
        count += 1
        corner[1] = -1

    return count, tuple(corner)

def createNewCCOAs(ccoaList, bestCCOA, products, units):
    #xoffset = bestCCOA.pos[0]-1
    #yoffset = bestCCOA.pos[1]-1
    unit = units[bestCCOA.unitIndex]

    xoffset = bestCCOA.pos[0] if bestCCOA.cornerType[0] > 0 else bestCCOA.pos[0]-products[bestCCOA.pIndex][0]
    yoffset = bestCCOA.pos[1] if bestCCOA.cornerType[1] > 0 else bestCCOA.pos[1]-products[bestCCOA.pIndex][1]

    sizeX = products[bestCCOA.pIndex][0]+2
    sizeY = products[bestCCOA.pIndex][1]+2

    for y in range(yoffset, yoffset+sizeY):
        if y >= 0 and y < unit.bag[1] and xoffset > 0:
            count, cType = countNeighbours(unit.bag, unit.mask, xoffset, y)
            corner = Corner(unitIndex=bestCCOA.unitIndex, pos=(xoffset,y), cornerType=cType)
            if count >= 2:
                for p in products:
                    if not p.isPlaced:
                        newccoa = createCCOA(corner, p, units)
                        if newccoa:
                            ccoaList.append(newccoa)

    for y in range(yoffset, yoffset+sizeY):
        if y >= 0 and y < unit.bag[1] and xoffset+sizeX-1 < unit.bag[0]:
            count, cType = countNeighbours(unit.bag, unit.mask, xoffset+sizeX-1, y)
            corner = Corner(unitIndex=bestCCOA.unitIndex, pos=(xoffset+sizeX-1,y), cornerType=cType)
            if count >= 2:
                for p in products:
                    if not p.isPlaced:
                        newccoa = createCCOA(corner, p, units)
                        if newccoa:
                            ccoaList.append(newccoa)

    for x in range(xoffset, xoffset+sizeX):
        if x >= 0 and x < unit.bag[0] and yoffset > 0:
            count, cType = countNeighbours(unit.bag, unit.mask, x, yoffset)
            corner = Corner(unitIndex=bestCCOA.unitIndex, pos=(x,yoffset), cornerType=cType)
            if count >= 2:
                for p in products:
                    if not p.isPlaced:
                        newccoa = createCCOA(corner, p, units)
                        if newccoa:
                            ccoaList.append(newccoa)

    for x in range(xoffset, xoffset+sizeX):
        if x >= 0 and x < unit.bag[0] and yoffset+sizeY-1 < unit.bag[1]:
            count, cType = countNeighbours(unit.bag, unit.mask, x, yoffset+sizeY-1)
            corner = Corner(unitIndex=bestCCOA.unitIndex, pos=(x,yoffset+sizeY-1), cornerType=cType)
            if count >= 2:
                for p in products:
                    if not p.isPlaced:
                        newccoa = createCCOA(corner, p, units)
                        if newccoa:
                            ccoaList.append(newccoa)



# For each rectangle, calc the list of CCOA an save all of them in L.
# A CCOA is a corner for a specific product. So maybe all n products fit in that corner
#   then there are n CCOAs. If only one product fits in there, this is one CCOA.
# Calculate C as Configuration (Mask) with all placed rectangles (Empty in the beginning).
#   For each CCOA in L, calc the degree.
#   Select the CCOA(i, x, y) with the highest degree.
#   Place rectangle i at x,y.
#   Remove all CCOAs involving rectangle i
#   Remove all infeasible CCOAs
#       If the to be placed rectangle doesn't fit any more (would now overlap rectangle i (!!!)).
#   Create new CCOA(s), if it is now possible to put any product into C, so that it touches rectangle i and something else.
#   Recalculate the degrees (including the new ones).
#
# If no rectangle can be placed inside C (L == []), CalcA0() returnes C (failure?).
# If all rectangles are successfully placed, CalcA0() returnes C (success).
#
# For a start: bag has to be empty!
def calcA0(units, ccoaList, products):

    #
    # Might it be possible, to calculate the best CCOA not just in the current bag, but overall?
    # So get calculate the highest ccoa over all possible bags. And then put the best one at its best position.
    # Next iteration calculate a little more (*bagCount) and put products even better?
    # I'll go at it after implementing A1. Maybe it is not possible any more...
    #
    while ccoaList:
        bestCCOA = recalculateDegrees(ccoaList, products, units)
        placeX = bestCCOA.pos[0] if bestCCOA.cornerType[0] > 0 else bestCCOA.pos[0]-products[bestCCOA.pIndex][0]+1
        placeY = bestCCOA.pos[1] if bestCCOA.cornerType[1] > 0 else bestCCOA.pos[1]-products[bestCCOA.pIndex][1]+1

        productToMask(units[bestCCOA.unitIndex].mask, products[bestCCOA.pIndex], placeX, placeY)
        removeAllInvalidCCOAs(ccoaList, bestCCOA, products, units)
        p = products[bestCCOA.pIndex]
        # pr2 == (x, y, width, height, value, index)
        placedProduct = (bestCCOA.pos[0], bestCCOA.pos[1], p.width, p.height, p.value, p.pIndex)
        units[bestCCOA.unitIndex].placedProducts.append(placedProduct)
        products[bestCCOA.pIndex] = Product(width=p.width, height=p.height, value=p.value, pIndex=p.pIndex, isPlaced=True)
        createNewCCOAs(ccoaList, bestCCOA, products, units)

def calcDensity(mask, bag):

    count = bag[0]*bag[1]
    setCount = 0
    for y in range(bag[1]):
        for x in range(bag[0]):
            if mask[y][x] != -1:
                setCount += 1

    return setCount / float(count)


def benefitA1(ccoa, units, ccoaList, products, rateValue):
    maskCopy = copy.deepcopy(units[ccoa.unitIndex].mask)
    ccoaListCopy = copy.deepcopy(ccoaList)
    productsCopy = copy.deepcopy(products)
    #placedProductsCopy = copy.deepcopy(units[ccoa.unitIndex].placedProducts)
    #unitsCopy = copy.deepcopy(units)
    unitsCopy = []
    for u in units:
        mCpy = copy.deepcopy(u.mask)
        bCpy = copy.deepcopy(u.bag)
        uCpy = copy.deepcopy(u.placedProducts)
        unitsCopy.append(Unit(mask=mCpy, bag=bCpy, placedProducts=uCpy))
    #unitCopy = Unit(mask=maskCopy, bag=units[ccoa.unitIndex].bag, placedProducts=placedProductsCopy)

    placeX = ccoa.pos[0] if ccoa.cornerType[0] > 0 else ccoa.pos[0]-productsCopy[ccoa.pIndex][0]+1
    placeY = ccoa.pos[1] if ccoa.cornerType[1] > 0 else ccoa.pos[1]-productsCopy[ccoa.pIndex][1]+1

    # Modify C by placing rectangle i at (x, y), and modify L;
    productToMask(maskCopy, productsCopy[ccoa.pIndex], placeX, placeY)
    removeAllInvalidCCOAs(ccoaListCopy, ccoa, productsCopy, unitsCopy)
    p = productsCopy[ccoa.pIndex]
    # pr2 == (x, y, width, height, value, index)
    placedProduct = (ccoa.pos[0], ccoa.pos[1], p.width, p.height, p.value, p.pIndex)
    unitsCopy[ccoa.unitIndex].placedProducts.append(placedProduct)
    productsCopy[ccoa.pIndex] = Product(width=p.width, height=p.height, value=p.value, pIndex=p.pIndex, isPlaced=True)
    createNewCCOAs(ccoaListCopy, ccoa, productsCopy, unitsCopy)

    calcA0(unitsCopy, ccoaListCopy, productsCopy)

    _, resultValue = maskToList(maskCopy, unitsCopy[ccoa.unitIndex].bag[0], unitsCopy[ccoa.unitIndex].bag[1], productsCopy, fillCosts)

    if rateValue:
        return resultValue
    else:
        return calcDensity(maskCopy, unitsCopy[ccoa.unitIndex].bag)

def calcA1(units, products, rateValue, verbose, lock, initiator, startTime):

    # Generate Configuraton
    ccoaList = []
    corners = []

    for unitIndex in range(len(units)):
        unit = units[unitIndex]
        corners.append( Corner(unitIndex=unitIndex, pos=(0,0), cornerType=(1,1)) )
        corners.append( Corner(unitIndex=unitIndex, pos=(unit.bag[0]-1,0), cornerType=(-1,1)) )
        corners.append( Corner(unitIndex=unitIndex, pos=(unit.bag[0]-1,unit.bag[1]-1), cornerType=(-1,-1)) )
        corners.append( Corner(unitIndex=unitIndex, pos=(0,unit.bag[1]-1), cornerType=(1,-1)) )

    bestCCOA = None
    # Generate CCOAs
    for product in products:
        if not product.isPlaced:
            for corner in corners:
                ccoa = createCCOA(corner, product, units)
                if ccoa:
                    ccoaList.append(ccoa)
                    if not bestCCOA:
                        bestCCOA = ccoa
                        continue
                    if ccoa.degree > bestCCOA.degree:
                        bestCCOA = ccoa
                        continue
                    if ccoa.degree == bestCCOA.degree:
                        if products[ccoa.pIndex].value > products[bestCCOA.pIndex].value:
                            bestCCOA = ccoa

    while ccoaList:
        maxBenefit = -1000000000000
        bestCCOA = None
        finished = False

        for ccoa in ccoaList:
            benefit = benefitA1(ccoa, units, ccoaList, products, rateValue)

            placedProductCount = 0
            for unit in units:
                placedProductCount += len(unit.placedProducts)
            finished = placedProductCount == len(products)

            if finished or not bestCCOA or benefit > maxBenefit:
                maxBenefit = benefit
                bestCCOA = ccoa
            if finished:
                break

        placeX = bestCCOA.pos[0] if bestCCOA.cornerType[0] > 0 else bestCCOA.pos[0]-products[bestCCOA.pIndex][0]+1
        placeY = bestCCOA.pos[1] if bestCCOA.cornerType[1] > 0 else bestCCOA.pos[1]-products[bestCCOA.pIndex][1]+1

        productToMask(units[bestCCOA.unitIndex].mask, products[bestCCOA.pIndex], placeX, placeY)
        removeAllInvalidCCOAs(ccoaList, bestCCOA, products, units)
        p = products[bestCCOA.pIndex]
        # pr2 == (x, y, width, height, value, index)
        placedProduct = (bestCCOA.pos[0], bestCCOA.pos[1], p.width, p.height, p.value, p.pIndex)
        units[bestCCOA.unitIndex].placedProducts.append(placedProduct)
        products[bestCCOA.pIndex] = Product(width=p.width, height=p.height, value=p.value, pIndex=p.pIndex, isPlaced=True)
        createNewCCOAs(ccoaList, bestCCOA, products, units)

        if verbose:
            resultList = [[] for x in range(len(units))]
            resultValue = 0
            for i in range(len(units)):
                unit = units[i]
                l, v = maskToList(unit.mask, unit.bag[0], unit.bag[1], products, fillCosts)
                resultList[i] = l
                resultValue += v
            printResult(lock, (resultList, resultValue), initiator, time.time()-startTime)

        if finished:
            calcA0(units, ccoaList, products)
            if verbose:
                resultList = [[] for x in range(len(units))]
                resultValue = 0
                for i in range(len(units)):
                    unit = units[i]
                    l, v = maskToList(unit.mask, unit.bag[0], unit.bag[1], products, fillCosts)
                    resultList[i] = l
                    resultValue += v
                printResult(lock, (resultList, resultValue), initiator, time.time()-startTime)
            return

    #return maskToList(unit.mask, unit.bag[0], unit.bag[1], products, fillCosts)

# This takes a lot of time to run... Complexity basically explodes through the roof...
# As I see it, there is no real benefit from the 3-4 examples tested. But there might be later on (?!?)
# This tries to optimise any product to any bag simultaneously.
# To find THE perfect spot for any given product.
def runA1Slow(bags, namedProducts, lock, fillCosts, initiator, rateValue, verbose, start):
    masks = []
    units = []

    for bIndex in range(len(bags)):
        bag = bags[bIndex]
        mask = createMask(bag)
        placedProducts = []

        units.append(Unit(bag=bag, mask=mask, placedProducts=placedProducts))

        masks.append(mask)

    calcA1(units, namedProducts, rateValue, verbose, lock, initiator, start)

    resultList = [[] for x in range(len(bags))]
    resultValue = 0
    for i in range(len(units)):
        unit = units[i]
        l, v = maskToList(unit.mask, unit.bag[0], unit.bag[1], namedProducts, fillCosts)
        resultList[i] = l
        resultValue += v

    printResult(lock, (resultList, resultValue), initiator, time.time()-start)


def runA1Fast(bags, products, lock, fillCosts, initiator, rateValue, verbose, start):

    resultList = [[] for x in range(len(bags))]
    resultValue = 0

    for bIndex in range(len(bags)):

        bag = bags[bIndex]
        mask = createMask(bag)
        placedProducts = []

        unit = Unit(bag=bag, mask=mask, placedProducts=placedProducts)
        units = [unit]

        calcA1(units, products, rateValue, False, lock, initiator, start)

        l, v = maskToList(unit.mask, unit.bag[0], unit.bag[1], products, fillCosts)

        resultList[bIndex] = l
        resultValue += v

        if verbose:
            restValue = reduce(lambda x,y: x - y[0]*y[1]*fillCosts, bags[bIndex+1:], 0)
            printResult(lock, (resultList, resultValue+restValue), initiator, time.time()-start)

    printResult(lock, (resultList, resultValue), initiator, time.time()-start)


#
# Here A0 tries to optimise by looking over all bags when trying to place one
# product. So the product can be placed in any bag at any time. So all bags are
# filled synchronously.
#
def runA0Slow(bags, products, lock, fillCosts, initiator, verbose, start):

    units = []

    for bIndex in range(len(bags)):
        bag = bags[bIndex]
        mask = createMask(bag)
        placedProducts = []

        units.append(Unit(bag=bag, mask=mask, placedProducts=placedProducts))

    # Generate Configuraton
    ccoaList = []
    corners = []

    for unitIndex in range(len(units)):
        unit = units[unitIndex]
        corners.append( Corner(unitIndex=unitIndex, pos=(0,0), cornerType=(1,1)) )
        corners.append( Corner(unitIndex=unitIndex, pos=(unit.bag[0]-1,0), cornerType=(-1,1)) )
        corners.append( Corner(unitIndex=unitIndex, pos=(unit.bag[0]-1,unit.bag[1]-1), cornerType=(-1,-1)) )
        corners.append( Corner(unitIndex=unitIndex, pos=(0,unit.bag[1]-1), cornerType=(1,-1)) )

    bestCCOA = None
    # Generate CCOAs
    for product in products:
        if not product.isPlaced:
            for corner in corners:
                ccoa = createCCOA(corner, product, units)
                if ccoa:
                    ccoaList.append(ccoa)
                    if not bestCCOA:
                        bestCCOA = ccoa
                        continue
                    if ccoa.degree > bestCCOA.degree:
                        bestCCOA = ccoa
                        continue
                    if ccoa.degree == bestCCOA.degree:
                        if products[ccoa.pIndex].value > products[bestCCOA.pIndex].value:
                            bestCCOA = ccoa
    calcA0(units, ccoaList, products)

    resultList = [[] for x in range(len(bags))]
    resultValue = 0
    for i in range(len(units)):
        unit = units[i]
        l, v = maskToList(unit.mask, unit.bag[0], unit.bag[1], products, fillCosts)
        resultList[i] = l
        resultValue += v

    printResult(lock, (resultList, resultValue), initiator, time.time()-start)

#
# Goes through every bag after each other and tries to fill the bag with
# the given products! Very fast because the loop over the bags does not downgrade
# the performance significantly.
#
def runA0Fast(bags, products, lock, fillCosts, initiator, verbose, start):

    resultList = [[] for x in range(len(bags))]
    resultValue = 0

    for bIndex in range(len(bags)):
        bag = bags[bIndex]
        mask = createMask(bag)
        placedProducts = []

        unit = Unit(bag=bag, mask=mask, placedProducts=placedProducts)
        units = [unit]

        # Generate Configuraton
        ccoaList = []
        corners = []

        corners.append( Corner(unitIndex=0, pos=(0,0), cornerType=(1,1)) )
        corners.append( Corner(unitIndex=0, pos=(unit.bag[0]-1,0), cornerType=(-1,1)) )
        corners.append( Corner(unitIndex=0, pos=(unit.bag[0]-1,unit.bag[1]-1), cornerType=(-1,-1)) )
        corners.append( Corner(unitIndex=0, pos=(0,unit.bag[1]-1), cornerType=(1,-1)) )

        bestCCOA = None
        # Generate CCOAs
        for product in products:
            if not product.isPlaced:
                for corner in corners:
                    ccoa = createCCOA(corner, product, units)
                    if ccoa:
                        ccoaList.append(ccoa)
                        if not bestCCOA:
                            bestCCOA = ccoa
                            continue
                        if ccoa.degree > bestCCOA.degree:
                            bestCCOA = ccoa
                            continue
                        if ccoa.degree == bestCCOA.degree:
                            if products[ccoa.pIndex].value > products[bestCCOA.pIndex].value:
                                bestCCOA = ccoa
        calcA0(units, ccoaList, products)

        l, v = maskToList(unit.mask, unit.bag[0], unit.bag[1], products, fillCosts)

        resultList[bIndex] = l
        resultValue += v

        if verbose:
            restValue = reduce(lambda x,y: x - y[0]*y[1]*fillCosts, bags[bIndex+1:], 0)
            printResult(lock, (resultList, resultValue+restValue), initiator, time.time()-start)

    printResult(lock, (resultList, resultValue), initiator, time.time()-start)

def infinitShuffle(products, bags, lock, fillCosts, initiator, start):
    while True:
        threads = []
        for i in range(4):
            shuffle(products)
            shuffle(bags)
            thread = Process(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts, initiator, True, start))
            threads.append(thread)
            thread.start()
        for t in threads:
            t.join()

def infiniteA1Fast(bags, namedProducts, lock, fillCosts, initiator, start):

    permutations = itertools.permutations(bags, len(bags))
    for p in permutations:
        runA1Fast(list(p), list(namedProducts), lock, fillCosts, initiator, True, True, start)

def infiniteA0Fast(bags, namedProducts, lock, fillCosts, initiator, start):

    permutations = itertools.permutations(bags, len(bags))
    for p in permutations:
        runA0Fast(list(p), list(namedProducts), lock, fillCosts, initiator, True, start)

def allEmptyBags(bags, fillCosts, lock, initiator, start):

    resultList = [[] for x in range(len(bags))]
    resultValue = reduce(lambda x,y: x - y[0]*y[1]*fillCosts, bags, 0)

    printResult(lock, (resultList, resultValue), initiator, time.time()-start)

if __name__ == '__main__':

    # [(width, height)]
    bags = eval(sys.stdin.readline())
    # [(width, height, value)]
    products = eval(sys.stdin.readline())
    # Cost for each fill-material (space in the output bags)
    fillCosts = eval(sys.stdin.readline())

    lock = Lock()
    threads = []

    start = time.time()

    # append index of the product to the tuple!
    products = [products[i]+(i,) for i in range(len(products))]
    bags = [bags[i]+(i,) for i in range(len(bags))]

    namedProducts = []
    for i in range(len(products)):
        p = products[i]
        products[i] = p+(i,)

        # Filter products out, if the value is worse than just fillCosts
        placed = False
        if p[2] <= p[0]*p[1]*-fillCosts:
            placed = True

        namedProducts.append(Product(width=p[0], height=p[1], value=p[2], pIndex=i, isPlaced=placed))

    if True:
        # Print all empty lists
        thread = Process(target=allEmptyBags, args=(list(bags), fillCosts, lock, "All_Empty", start))
        threads.append(thread)
        thread.start()

    if True:
        #if len(bags) <= 10:
        # A1 slow!
        thread = Process(target=runA1Slow, args=(list(bags), list(namedProducts), lock, fillCosts, "A1_Slow_Value", True, True, start))
        threads.append(thread)
        thread.start()

        # A1 fast - Trying all possible bag-combinations!
        thread = Process(target=infiniteA1Fast, args=(bags, namedProducts, lock, fillCosts, "A1_Fast_Value", start))
        threads.append(thread)
        thread.start()

        # A0 fast - Trying all possible bag-combinations!
        thread = Process(target=infiniteA0Fast, args=(bags, namedProducts, lock, fillCosts, "A0_Fast", start))
        threads.append(thread)
        thread.start()

        # A0 slow!
        thread = Process(target=runA0Slow, args=(list(bags), list(namedProducts), lock, fillCosts, "A0_Slow", True, start))
        threads.append(thread)
        thread.start()


    if True:
        # Shuffles both bags and products forever
        thread = Process(target=infinitShuffle, args=(list(products), list(bags), lock, fillCosts, "Infinite_Shuffle", start))
        threads.append(thread)
        thread.start()

        # Smallest values first
        products = sorted(products, key=lambda x: x[2], reverse=False)
        thread = Process(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts, "p_sort_v_I", True, start))
        threads.append(thread)
        thread.start()

        # Biggest values first
        products = sorted(products, key=lambda x: x[2], reverse=True)
        thread = Process(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts, "p_sort_v_rev_I", True, start))
        threads.append(thread)
        thread.start()

        # Biggest products first
        products = sorted(products, key=lambda x: x[0]*x[1], reverse=True)
        thread = Process(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts, "p_sort_s_rev_I", True, start))
        threads.append(thread)
        thread.start()

        # Biggest bags first
        bags = sorted(bags, key=lambda x: x[0]*x[1], reverse=True)
        thread = Process(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts, "b_sort_s_rev_I", True, start))
        threads.append(thread)
        thread.start()

        for rate in range(1, 100, 5):
            # Biggest products combined with biggest values ???
            products = sorted(products, key=lambda x: x[0]*x[1] + rate*x[2], reverse=True)
            thread = Process(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts, "p_sort_sv_rev_I", True, start))
            threads.append(thread)
            thread.start()

    for t in threads:
        t.join()


