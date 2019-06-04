#!/usr/bin/python3

import tree
import xlsParser

filename = '../data/IrisDataMultiples.xls'

agds = tree.create_tree(filename)
[data, columns] = xlsParser.read_xls_iris(filename)

tree.median_benchmark(agds, data)
tree.average_benchmark(agds, data)