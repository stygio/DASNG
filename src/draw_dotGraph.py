#!/usr/bin/python3

import tree
filename = '../data/IrisData.xls'

agds = tree.create_tree(filename)
dot = agds.generate_dotGraph()