#!/usr/bin/python3

import tree

path_to_data = '../data/'
filename = 'IrisData.xls'
path_to_file = path_to_data + filename

agds = tree.create_tree(path_to_file)
dot = agds.generate_dotGraph()