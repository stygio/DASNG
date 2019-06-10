#!/usr/bin/python3

import tree

filename = '../data/IrisData.xls'

agds = tree.create_AGDS(filename)
tree.sort_by_similarity(agds)