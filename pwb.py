#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from threading import Thread
from thread import allocate_lock
from random import shuffle

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

    if True:
        for i in range(100):
            shuffle(products)
            thread = Thread(target=calcGreedyFilling, args=(lock, placeProductInBagDumb, list(bags), list(products), fillCosts,))
            threads += [thread]
            thread.start()

        for i in range(100):
            shuffle(bags)
            thread = Thread(target=calcGreedyFilling, args=(lock, placeProductInBagDumb, list(bags), list(products), fillCosts,))
            threads += [thread]
            thread.start()

        products = sorted(products, key=lambda x: x[2], reverse=False)
        thread = Thread(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts,))
        threads += [thread]
        thread.start()

    products = sorted(products, key=lambda x: x[2], reverse=True)
    thread = Thread(target=calcGreedyFilling, args=(lock, placeProductInBagIntelligent, list(bags), list(products), fillCosts,))
    threads += [thread]
    thread.start()

    # - Shuffle products (shuffle back)
    # - Shuffle bags (and shuffle back)
    # - Sort bags on size (and sort back)
    # - Sort products on value (ascending/descending) (sort back!)
    # - Sort products on size (ascending/descending) (sort back!)
    # - Sort bags (ascending/descending) (and sort back)
    # - Delete all products with value < -fillCosts
    # -

    for t in threads:
        t.join()


