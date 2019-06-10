#!/usr/bin/python3

import tree
import dataParser

filename = '../data/IrisDataMultiples.xls'

agds = tree.create_AGDS(filename)
[data, columns] = dataParser.read_xls_iris(filename)

tree.median_benchmark(agds, data)
tree.average_benchmark(agds, data)