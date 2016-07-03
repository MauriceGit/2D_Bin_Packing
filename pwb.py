#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from threading import Thread
from thread import allocate_lock
from random import shuffle
import math

import collections
import copy

# Best global score
bestScore = -9999999999999999999999999999999999

# Tuple of (list, resultValue)
def printResult(lock, result):
    lock.acquire()
    global bestScore
    if result[1] > bestScore:
        bestScore = result[1]
        print bestScore, result[0]
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


# Der hier ist eeetwas besser, aber nicht viel.
# Hier amch ich prinzipiell das Gleiche, wie bei dem Dummen Algorithmus.
# Mit dem Unterschied, dass ich versuche, dass mindestens 2 Seiten vollen Kontakt mit irgendwas haben.
# Also eine Ecke zum Beispiel. Ja? Jupp
# Und wenn ich zwei Seiten habe, return ich das.
# Try to get at most outer blocks aligned with other blocks or the side
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


def calcGreedyFilling(lock, algorithm, bags, products, fillCosts):

    resultList = [[] for x in range(len(bags))]
    resultValue = 0

    savedProducts = sorted(list(products), key=lambda x: x[3])

    for bag in bags:
        res, value = fillBag(algorithm, bag, products, savedProducts, fillCosts)
        #print value
        # put the calculated bag to the right position (just like they came in originally!)
        resultList[bag[2]] = res
        resultValue += value

    printResult(lock, (resultList, resultValue) )


########################################################################
#### A two-level search algorithm for 2D rectangular packing problem ###
########################################################################

CCOA = collections.namedtuple('CCOA', 'pos cornerType pIndex degree')
Corner = collections.namedtuple('Corner', 'pos cornerType')
Product = collections.namedtuple('Product', 'width height value pIndex isPlaced')

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


def recalculateDegrees(ccoaList, placedProducts, products, bag):
    bestCCOA = None
    for i in range(len(ccoaList)):
        ccoa = ccoaList[i]
        dg = calcDegree(ccoa.pos[0], ccoa.pos[1], ccoa.cornerType, products[ccoa.pIndex], placedProducts, bag)
        newCCOA = CCOA(pos=ccoa.pos, cornerType=ccoa.cornerType, pIndex=ccoa.pIndex, degree=dg)
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
def createCCOA(corner, product, mask, placedProducts, bag):

    # Iterate the outline of the product on the mask on the corner-position.
    # If it hits something, return None. Otherwise create a SSOA.

    placeX = corner.pos[0] if corner.cornerType[0] > 0 else corner.pos[0]-product[0]+1
    placeY = corner.pos[1] if corner.cornerType[1] > 0 else corner.pos[1]-product[1]+1

    if productFitsFast(mask, product, placeX, placeY, bag):
        pDegree = calcDegree(corner.pos[0], corner.pos[1], corner.cornerType, product, placedProducts, bag)
        return CCOA(pos=corner.pos, cornerType=corner.cornerType, pIndex=product[3], degree=pDegree)
    else:
        return None

def removeAllInvalidCCOAs(ccoas, placedccoa, products, mask, bag):
    toDelete = []
    for i in range(len(ccoas)):
        ccoa = ccoas[i]
        if ccoa.pos == placedccoa.pos or ccoa.pIndex == placedccoa.pIndex:
            toDelete.append(i)
            continue

        placeX = ccoa.pos[0] if ccoa.cornerType[0] > 0 else ccoa.pos[0]-products[ccoa.pIndex][0]+1
        placeY = ccoa.pos[1] if ccoa.cornerType[1] > 0 else ccoa.pos[1]-products[ccoa.pIndex][1]+1

        if not productFitsFast(mask, products[ccoa.pIndex], placeX, placeY, bag):
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

def createNewCCOAs(ccoaList, bestCCOA, products, mask, bag, placedProducts):
    #xoffset = bestCCOA.pos[0]-1
    #yoffset = bestCCOA.pos[1]-1

    xoffset = bestCCOA.pos[0] if bestCCOA.cornerType[0] > 0 else bestCCOA.pos[0]-products[bestCCOA.pIndex][0]
    yoffset = bestCCOA.pos[1] if bestCCOA.cornerType[1] > 0 else bestCCOA.pos[1]-products[bestCCOA.pIndex][1]

    sizeX = products[bestCCOA.pIndex][0]+2
    sizeY = products[bestCCOA.pIndex][1]+2

    for y in range(yoffset, yoffset+sizeY):
        if y >= 0 and y < bag[1] and xoffset > 0:
            count, cType = countNeighbours(bag, mask, xoffset, y)
            corner = Corner(pos=(xoffset,y), cornerType=cType)
            if count >= 2:
                for p in products:
                    if not p.isPlaced:
                        newccoa = createCCOA(corner, p, mask, placedProducts, bag)
                        if newccoa:
                            ccoaList.append(newccoa)

    for y in range(yoffset, yoffset+sizeY):
        if y >= 0 and y < bag[1] and xoffset+sizeX-1 < bag[0]:
            count, cType = countNeighbours(bag, mask, xoffset+sizeX-1, y)
            corner = Corner(pos=(xoffset+sizeX-1,y), cornerType=cType)
            if count >= 2:
                for p in products:
                    if not p.isPlaced:
                        newccoa = createCCOA(corner, p, mask, placedProducts, bag)
                        if newccoa:
                            ccoaList.append(newccoa)

    for x in range(xoffset, xoffset+sizeX):
        if x >= 0 and x < bag[0] and yoffset > 0:
            count, cType = countNeighbours(bag, mask, x, yoffset)
            corner = Corner(pos=(x,yoffset), cornerType=cType)
            if count >= 2:
                for p in products:
                    if not p.isPlaced:
                        newccoa = createCCOA(corner, p, mask, placedProducts, bag)
                        if newccoa:
                            ccoaList.append(newccoa)

    for x in range(xoffset, xoffset+sizeX):
        if x >= 0 and x < bag[0] and yoffset+sizeY-1 < bag[1]:
            count, cType = countNeighbours(bag, mask, x, yoffset+sizeY-1)
            corner = Corner(pos=(x,yoffset+sizeY-1), cornerType=cType)
            if count >= 2:
                for p in products:
                    if not p.isPlaced:
                        newccoa = createCCOA(corner, p, mask, placedProducts, bag)
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
def calcA0(mask, bag, ccoaList, products, placedProducts):

    #
    # Might it be possible, to calculate the best CCOA not just in the current bag, but overall?
    # So get calculate the highest ccoa over all possible bags. And then put the best one at its best position.
    # Next iteration calculate a little more (*bagCount) and put products even better?
    # I'll go at it after implementing A1. Maybe it is not possible any more...
    #
    while ccoaList:
        bestCCOA = recalculateDegrees(ccoaList, placedProducts, products, bag)
        placeX = bestCCOA.pos[0] if bestCCOA.cornerType[0] > 0 else bestCCOA.pos[0]-products[bestCCOA.pIndex][0]+1
        placeY = bestCCOA.pos[1] if bestCCOA.cornerType[1] > 0 else bestCCOA.pos[1]-products[bestCCOA.pIndex][1]+1

        productToMask(mask, products[bestCCOA.pIndex], placeX, placeY)
        removeAllInvalidCCOAs(ccoaList, bestCCOA, products, mask, bag)
        p = products[bestCCOA.pIndex]
        # pr2 == (x, y, width, height, value, index)
        placedProduct = (bestCCOA.pos[0], bestCCOA.pos[1], p.width, p.height, p.value, p.pIndex)
        placedProducts.append(placedProduct)
        products[bestCCOA.pIndex] = Product(width=p.width, height=p.height, value=p.value, pIndex=p.pIndex, isPlaced=True)
        createNewCCOAs(ccoaList, bestCCOA, products, mask, bag, placedProducts)

    # All products are successfully placed!
    return len(products) == len(placedProducts)
    #return maskToList(mask, bag[0], bag[1], products, fillCosts), mask

def calcDensity(mask, bag):

    count = bag[0]*bag[1]
    setCount = 0
    for y in range(bag[1]):
        for x in range(bag[0]):
            if mask[y][x] != -1:
                setCount += 1

    return setCount / float(count)



#
#
#
def benefitA1(ccoa, mask, bag, ccoaList, products, placedProducts):
    maskCopy = copy.deepcopy(mask)
    ccoaListCopy = copy.deepcopy(ccoaList)
    productsCopy = copy.deepcopy(products)
    placedProductsCopy = copy.deepcopy(placedProducts)

    placeX = ccoa.pos[0] if ccoa.cornerType[0] > 0 else ccoa.pos[0]-productsCopy[ccoa.pIndex][0]+1
    placeY = ccoa.pos[1] if ccoa.cornerType[1] > 0 else ccoa.pos[1]-productsCopy[ccoa.pIndex][1]+1

    # Modify C by placing rectangle i at (x, y), and modify L;
    productToMask(maskCopy, productsCopy[ccoa.pIndex], placeX, placeY)
    removeAllInvalidCCOAs(ccoaListCopy, ccoa, productsCopy, maskCopy, bag)
    p = productsCopy[ccoa.pIndex]
    # pr2 == (x, y, width, height, value, index)
    placedProduct = (ccoa.pos[0], ccoa.pos[1], p.width, p.height, p.value, p.pIndex)
    placedProductsCopy.append(placedProduct)
    productsCopy[ccoa.pIndex] = Product(width=p.width, height=p.height, value=p.value, pIndex=p.pIndex, isPlaced=True)
    createNewCCOAs(ccoaListCopy, ccoa, productsCopy, maskCopy, bag, placedProductsCopy)

    success = calcA0(maskCopy, bag, ccoaListCopy, productsCopy, placedProductsCopy)

    _, resultValue = maskToList(maskCopy, bag[0], bag[1], productsCopy, fillCosts)

    density = calcDensity(maskCopy, bag)

    return resultValue, success
    #return density, success

def calcA1(bag, products, fillCosts):

    # Generate Configuraton
    mask = createMask(bag)
    ccoaList = []
    placedProducts = []
    corners = [ Corner(pos=(0,0), cornerType=(1,1)) ]
    corners.append( Corner(pos=(bag[0]-1,0), cornerType=(-1,1)) )
    corners.append( Corner(pos=(bag[0]-1,bag[1]-1), cornerType=(-1,-1)) )
    corners.append( Corner(pos=(0,bag[1]-1), cornerType=(1,-1)) )

    bestCCOA = None
    # Generate CCOAs
    for p in products:
        if not p.isPlaced:
            for c in corners:
                ccoa = createCCOA(c, p, mask, placedProducts, bag)
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
            benefit, success = benefitA1(ccoa, mask, bag, ccoaList, products, placedProducts)
            finished = success
            if finished or not bestCCOA or benefit > maxBenefit:
                maxBenefit = benefit
                bestCCOA = ccoa
            if finished:
                break

        placeX = bestCCOA.pos[0] if bestCCOA.cornerType[0] > 0 else bestCCOA.pos[0]-products[bestCCOA.pIndex][0]+1
        placeY = bestCCOA.pos[1] if bestCCOA.cornerType[1] > 0 else bestCCOA.pos[1]-products[bestCCOA.pIndex][1]+1

        productToMask(mask, products[bestCCOA.pIndex], placeX, placeY)
        removeAllInvalidCCOAs(ccoaList, bestCCOA, products, mask, bag)
        p = products[bestCCOA.pIndex]
        # pr2 == (x, y, width, height, value, index)
        placedProduct = (bestCCOA.pos[0], bestCCOA.pos[1], p.width, p.height, p.value, p.pIndex)
        placedProducts.append(placedProduct)
        products[bestCCOA.pIndex] = Product(width=p.width, height=p.height, value=p.value, pIndex=p.pIndex, isPlaced=True)
        createNewCCOAs(ccoaList, bestCCOA, products, mask, bag, placedProducts)

        if finished:
            success = calcA0(mask, bag, ccoaList, products, placedProducts)
            break

    return maskToList(mask, bag[0], bag[1], products, fillCosts), mask

def runA1(bags, namedProducts, lock, fillCosts):

    resultList = [[] for x in range(len(bags))]
    resultValue = 0

    masks = []

    for bag in bags:
        entry = calcA1(bag, namedProducts, fillCosts)
        res, value, mask = entry[0][0], entry[0][1], entry[1]
        # put the calculated bag to the right position (just like they came in originally!)
        resultList[bag[2]] = res
        resultValue += value
        masks.append(mask)

    printResult(lock, (resultList, resultValue) )

    if False:
        print "========================================================="
        for i in range(len(masks)):
            ppMask(masks[i], bags[i])
            print "========================================================="



if __name__ == '__main__':

    # [(width, height)]
    bags = eval(sys.stdin.readline())
    # [(width, height, value)]
    products = eval(sys.stdin.readline())
    # Cost for each fill-material (space in the output bags)
    fillCosts = eval(sys.stdin.readline())

    lock = allocate_lock()
    threads = []

    # append index of the product to the tuple!
    products = [products[i]+(i,) for i in range(len(products))]
    bags = [bags[i]+(i,) for i in range(len(bags))]

    namedProducts = []
    for p in products:
        namedProducts.append(Product(width=p[0], height=p[1], value=p[2], pIndex=p[3], isPlaced=False))

    for i in range(1):
        runA1(list(bags), list(namedProducts), lock, fillCosts)

    if False:
        for i in range(10):
            shuffle(products)
            shuffle(bags)
            thread = Thread(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts,))
            threads += [thread]
            thread.start()

        products = sorted(products, key=lambda x: x[2], reverse=False)
        thread = Thread(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts,))
        threads += [thread]
        thread.start()

        # Biggest values first
        products = sorted(products, key=lambda x: x[2], reverse=True)
        thread = Thread(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts,))
        threads += [thread]
        thread.start()

        # Biggest products first
        products = sorted(products, key=lambda x: x[0]*x[1], reverse=True)
        thread = Thread(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts,))
        threads += [thread]
        thread.start()

        # Biggest bags first
        bags = sorted(bags, key=lambda x: x[0]*x[1], reverse=True)
        thread = Thread(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts,))
        threads += [thread]
        thread.start()

        # Biggest products combined with biggest values ???
        products = sorted(products, key=lambda x: x[0]*x[1] + 10*x[2], reverse=True)
        thread = Thread(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts,))
        threads += [thread]
        thread.start()

    # - Sort products on value (ascending/descending) (sort back!)
    # - Sort products on size (ascending/descending) (sort back!)
    # - Sort bags (ascending/descending) (and sort back)
    # - Delete all products with value < -fillCosts
    # -

    for t in threads:
        t.join()


