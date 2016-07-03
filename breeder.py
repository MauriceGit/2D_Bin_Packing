#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# file: breeder.py
# author: Hanno Sternberg

import argparse
import random


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Brahmin Breeder")
    parser.add_argument("--pouch-count",
                        type=int, nargs=2,
                        default=(1, 3))
    parser.add_argument("--pouch-size",
                        type=int, nargs=2,
                        default=(8, 25))
    parser.add_argument("--package-count",
                        type=int, nargs=2,
                        default=(10, 100))
    parser.add_argument("--package-size",
                        type=int, nargs=2,
                        default=(1, 10))
    parser.add_argument("--package-value",
                        type=int, nargs=2,
                        default=(1, 5))
    parser.add_argument("--waste-cost",
                        type=int, nargs=2,
                        default=(0, 3))

    args = parser.parse_args()

    pouchCount = random.randint(*args.pouch_count)
    packageCount = random.randint(*args.package_count)
    print([
        (random.randint(*args.pouch_size),
         random.randint(*args.pouch_size)
         ) for _ in range(pouchCount)
    ])
    print([
        (random.randint(*args.package_size),
         random.randint(*args.package_size),
         random.randint(*args.package_value)
         ) for _ in range(packageCount)
    ])
    print(random.randint(*args.waste_cost))



