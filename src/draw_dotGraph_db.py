#!/usr/bin/python3

import tree

path_to_data = '../data/'
filename = 'university.db'
path_to_file = path_to_data + filename

dasng = tree.create_DASNG(path_to_file)
dot = dasng.generate_dotGraph()