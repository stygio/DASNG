import numpy as np
from graphviz import Digraph, Graph


class Tree:
	def __init__(self, tree_type, attributes=[], samples=[]):
		self.tree_type = tree_type
		self.attributes = attributes
		self.samples = samples
		self.link_samples()

	def link_samples(self):
		if self.samples != None:
			if self.tree_type == 'AGDS':
				for attribute in range(len(self.attributes)):
					for sample in range(len(self.samples)):
						self.samples[sample].nodes[attribute].avb_node = self.attributes[attribute].avb_tree.findElement(self.samples[sample].nodes[attribute].value)
			elif self.tree_type == 'DASNG':
				return 0

	def generate_dotGraph(self):
		dotGraph = Digraph(comment = 'Dot Graph', format = 'svg')
		dotGraph.attr(splines = 'spline', pack = 'false', minlen='100.0')
		if self.samples != None:
			if self.tree_type == 'AGDS':
				for sample in range(len(self.samples)):
					dotGraph.node(self.samples[sample].uniqueID, self.samples[sample].name)
			elif self.tree_type == 'DASNG':
				for i in range(len(self.samples)):
					with dotGraph.subgraph(name = "cluster_" + self.samples[i][0]) as dotSub:
						dotSub.attr(style='filled')
						dotSub.attr(color='lightgrey')
						dotSub.node_attr.update(style='filled', color='white')
						dotSub.attr(label=self.samples[i][0])
						for j in range(len(self.samples[i][1])):
							dotSub.node(self.samples[i][1][j].uniqueID, self.samples[i][1][j].name)
				for i in range(len(self.samples)):
					for j in range(len(self.samples[i][1])):
						for k in range(len(self.samples[i][1][j].foreign_samples)):
							dotGraph.edge(self.samples[i][1][j].uniqueID, self.samples[i][1][j].foreign_samples[k].uniqueID)
		for attribute in range(len(self.attributes)):
			with dotGraph.subgraph(name = "cluster_" + self.attributes[attribute].name) as dotSub:
				dotSub.attr(style='filled')
				dotSub.attr(color='lightgrey')
				dotSub.node_attr.update(style='filled', color='white')
				self.attributes[attribute].add_to_dotGraph(dotSub)
				dotSub.attr(label=self.attributes[attribute].name)
		dotGraph.render()
		return dotGraph


class Sample:
	def __init__(self, name, nodes = [], foreign_samples = []):
		self.uniqueID = str(id(self))
		self.name = name
		self.nodes = nodes
		self.nr_nodes = len(self.nodes)
		self.foreign_samples = foreign_samples
		self.similarity = 0

	def add_nodes(self, node):
		if type(node) != list:
			self.nodes.append(node)
		else:
			self.nodes.extend(node)
		self.nr_nodes = len(self.nodes)

	def add_foreign_samples(self, foreign_samples):
		if type(foreign_samples) != list:
			self.foreign_samples.append(foreign_samples)
		else:
			self.foreign_samples.extend(foreign_samples)

	def value_string(self):
		retString = "{0} | ".format(self.name)
		for i in range(self.nr_nodes):
			retString += "{0}: {1}".format(self.nodes[i].attribute, self.nodes[i].value)
			if i < self.nr_nodes - 1:
				retString += ", "
		return retString

	def calculate_similarity(self, values = [], sample = None):
		if values:
			self.similarity = 0
			for i in range(self.nr_nodes):
				if type(values[i]) != str:
					self.similarity += (1 - abs(values[i] - self.nodes[i].value)/(self.nodes[i].avb_node.root().getMax().keys[-1].value - self.nodes[i].avb_node.root().getMin().keys[0].value))/self.nr_nodes
				else:
					if values[i] == self.nodes[i].value:
						self.similarity += 1/self.nr_nodes
		elif sample != None:
			self.similarity = 0
			for i in range(self.nr_nodes):
				if type(sample.nodes[i].value) != str:
					self.similarity += (1 - abs(sample.nodes[i].value - self.nodes[i].value)/(self.nodes[i].avb_node.root().getMax().keys[-1].value - self.nodes[i].avb_node.root().getMin().keys[0].value))/self.nr_nodes
				else:
					if sample.nodes[i].value == self.nodes[i].value:
						self.similarity += 1/self.nr_nodes


class Node:
	def __init__(self, attribute, value, samples = [], avb_node = None):
		self.attribute = attribute
		self.value = value
		self.samples = samples
		self.nr_samples = len(self.samples)
		self.avb_node = avb_node

	def add_objects(self, sample):
		# Add checking for duplicates
		if type(sample) != list:
			self.samples.append(sample)
		else:
			self.samples.extend(sample)
		self.nr_samples = len(self.samples)


class Attribute:
	def __init__(self, name, nodes):
		self.uniqueID = str(id(self))
		self.name = name
		self.nr_samples = 0
		self.avb_tree = AvbTree(attribute = self, nodes = nodes)

	def insert(self, node):
		self.avb_tree.insert(node)

	def getMin(self):
		return self.avb_tree.root.getMin()

	def getMax(self):
		return self.avb_tree.root.getMax()

	def findElement(self, searchedValue):
		return self.avb_tree.root.findElement(searchedValue)

	def add_to_dotGraph(self, dotGraph):
		dotGraph.node(self.uniqueID, self.name)
		dotGraph.node(self.avb_tree.root.uniqueID, self.avb_tree.root.value_string())
		dotGraph.edge(self.uniqueID, self.avb_tree.root.uniqueID)
		self.avb_tree.root.add_to_dotGraph(dotGraph)

	def calculateAverage(self):
		return self.avb_tree.calculateAverage()

	def getMedian(self):
		return self.avb_tree.getMedian()


class AvbTree:
	def __init__(self, attribute, nodes=[]):
		self.attribute = attribute
		self.root = None
		self.median = None
		self.construction(nodes)

	def construction(self, nodes):
		# Declare root as nodes[0], then add_keys to it from based on nodes in a loop
		if type(nodes) == list:
			self.root = AvbNode(node = nodes[0], parent = None, avb_tree = self)
			self.attribute.nr_samples += nodes[0].nr_samples
			for i in range(1, len(nodes)):
				self.insert(nodes[i])
		# If it's just a single item, simply make it the root
		else:
			self.attribute.nr_samples += nodes.nr_samples
			self.root = AvbNode(node = nodes, parent = None)

	def insert(self, node):
		self.attribute.nr_samples += node.nr_samples
		self.root.add_key_to_tree(node)

	def getMin(self):
		return self.root.getMin()

	def getMax(self):
		return self.root.getMax()

	def findElement(self, searchedValue):
		return self.root.findElement(searchedValue)

	def calculateAverage(self):
		if type(self.root.keys[0].value):
			total = 0
			total = self.root.calculateAverage(total = total)
			return total / self.attribute.nr_samples
		else:
			return 0

	def getMedian(self):
		self.root.getMedian(median_sample_index = self.attribute.nr_samples/2 + 0.5, current_index = 0)
		return self.median

class AvbNode:
	def __init__(self, parent, node = None, left = None, middle = None, right = None, avb_node = None, avb_tree = None):
		self.uniqueID = str(id(self))
		self.parent = parent
		self.avb_tree = avb_tree
		if avb_node == None:
			self.attribute = node.attribute
			self.keys = [node]
			self.left = left
			self.middle = middle
			self.right = right
		else:
			self.attribute = avb_node.attribute
			self.keys = avb_node.keys
			self.left = avb_node.left
			if self.left != None:
				self.left.parent = self
			self.middle = avb_node.middle
			if self.middle != None:
				self.middle.parent = self
			self.right = avb_node.right
			if self.right != None:
				self.right.parent = self

	def getMin(self):
		return self.left.getMin() if self.left != None else self

	def getMax(self):
		return self.right.getMax() if self.right != None else self

	def findElement(self, searchedValue):
		# Check if the value is in this node
		for i in range(len(self.keys)):
			if searchedValue == self.keys[i].value:
				return self
		if searchedValue < self.keys[0].value:
			if self.left != None:	
				return self.left.findElement(searchedValue)
		elif searchedValue > self.keys[-1].value:
			if self.right != None:	
				return self.right.findElement(searchedValue)
		else:
			if self.middle != None:
				return self.middle.findElement(searchedValue)

	def calculateAverage(self, total):
		for i in range(len(self.keys)):
			total += self.keys[i].value * self.keys[i].nr_samples
		if self.left != None:
			total = self.left.calculateAverage(total)
		if self.middle != None:
			total= self.middle.calculateAverage(total)
		if self.right != None:
			total = self.right.calculateAverage(total)
		return total

	def getMedian(self, median_sample_index, current_index):
		# Not quite correct
		if self.left != None:
			current_index = self.left.getMedian(median_sample_index, current_index)
		
		if median_sample_index%1 == 0.5:
			if current_index < median_sample_index-1 and current_index + self.keys[0].nr_samples >= median_sample_index - 0.5:
				self.root().avb_tree.median = self.keys[0].value
			elif current_index + self.keys[0].nr_samples == median_sample_index + 0.5:
				self.root().avb_tree.median = (self.root().avb_tree.median + self.keys[0].value) / 2
		else:
			if current_index < median_sample_index and current_index + self.keys[0].nr_samples >= median_sample_index:
				self.root().avb_tree.median = self.keys[0].value
		current_index += self.keys[0].nr_samples
		
		if self.middle != None:
			current_index = self.middle.getMedian(median_sample_index, current_index)
		
		if len(self.keys) == 2:
			if median_sample_index%1 == 0.5:
				if current_index < median_sample_index-1 and current_index + self.keys[1].nr_samples >= median_sample_index - 0.5:
					self.root().avb_tree.median = self.keys[1].value
				elif current_index + self.keys[1].nr_samples == median_sample_index + 0.5:
					self.root().avb_tree.median = (self.root().avb_tree.median + self.keys[1].value) / 2
			else:
				if current_index < median_sample_index and current_index + self.keys[1].nr_samples >= median_sample_index:
					self.root().avb_tree.median = self.keys[1].value
			current_index += self.keys[1].nr_samples
		
		if self.right != None:
			current_index = self.right.getMedian(median_sample_index, current_index)

		return current_index

	def root(self):
		if self.parent != None:
			retVal = self.parent.root()
			return retVal
		else:
			return self

	def print_values(self):
		for i in range(len(self.keys)):
			print("Key {0}: {1}; Counter: {2}".format(i, self.keys[i].value, self.keys[i].nr_samples))

	def value_string(self):
		if len(self.keys) == 1:
			retVal = "{0}\n{1}".format(self.keys[0].nr_samples, self.keys[0].value)
		else:
			retVal = "{0} | {1}\n{2} | {3}".format(self.keys[0].nr_samples, self.keys[1].nr_samples, self.keys[0].value, self.keys[1].value)
		return retVal

	def remove_self_from_parent(self):
		if self.parent.left == self:
			self.parent.left = None
		elif self.parent.middle == self:
			self.parent.middle = None
		elif self.parent.right == self:
			self.parent.right = None

	def make_subNode(self, node):
		self.add_key_to_node(node)
		if len(self.keys) > 2:
			self.left = AvbNode(node = self.keys[0], parent = self)
			self.right = AvbNode(node = self.keys[2], parent = self)
			del self.keys[2]
			del self.keys[0]
			# Check if the node has a parent (otherwise it is the root)
			if self.parent != None:
				self.remove_self_from_parent()
				self.parent.node_handler(self)

	def add_key_to_node(self, node):
		# New value is less than the lowest
		if node.value < self.keys[0].value:
			self.keys = [node] + self.keys
		# New value belongs in the middle
		elif node.value > self.keys[0].value and node.value < self.keys[-1].value:
			self.keys = [self.keys[0], node, self.keys[1]]
		# New value is the largest
		elif node.value > self.keys[-1].value:
			self.keys.append(node)

	def add_key_to_tree(self, node):
		# # Storing amount of new samples
		# if self == self.root():
		# 	self.avb_tree.attribute.nr_samples += node.nr_samples
		# Check if inserted key matches the value of existing keys
		is_inserted_key_a_duplicate = 0
		for i in range(len(self.keys)):
			if node.value == self.keys[i].value:
				self.keys[i].add_objects(node.samples)
				is_inserted_key_a_duplicate = 1
		# Inserted key doesn't match the value of keys in this node
		if not is_inserted_key_a_duplicate:
			# Less than the left-most key
			if node.value < self.keys[0].value:
				# No left child node exists (this is the lowest leaf)
				if self.left == None:
					self.make_subNode(node)
				# Left child exists, go down the left edge
				else:
					self.left.add_key_to_tree(node)
			# More than left-most key and less than right-most key
			elif node.value > self.keys[0].value and node.value < self.keys[-1].value:
				# No middle child node exists (this is the lowest leaf)
				if self.middle == None:
					self.make_subNode(node)
				# Middle child exists, go down the middle
				else:
					self.middle.add_key_to_tree(node)
			# More than the right-most key
			elif node.value > self.keys[-1].value:
				# No right child node exists (this is the lowest leaf)
				if self.right == None:
					self.make_subNode(node)
				# Right child exists, go down the right edge
				else:
					self.right.add_key_to_tree(node)

	def node_handler(self, avb_node):
		# Add the received 'middle' value to this node's keys
		self.add_key_to_node(avb_node.keys[0])
	
		# Behavior if node now has 2 keys
		if len(self.keys) == 2:
			# Checking where the pointers from passed avb_node belong			
			# Left pointer
			if avb_node.left.keys[0].value < self.keys[0].value:
				# If no left connection exists, create it
				if self.left == None:
					self.left = AvbNode(avb_node = avb_node.left, parent = self)
				else:
					self.left.add_key_to_node(avb_node.left.keys[0])
			elif avb_node.left.keys[0].value > self.keys[0].value and avb_node.left.keys[0].value < self.keys[1].value:
				# If no middle connection exists, create it
				if self.middle == None:
					self.middle = AvbNode(avb_node = avb_node.left, parent = self)
				else:
					self.middle.add_key_to_node(avb_node.left.keys[0])
			else:
				# If no right connection exists, create it
				if self.right == None:
					self.right = AvbNode(avb_node = avb_node.left, parent = self)
				else:
					self.right.add_key_to_node(avb_node.left.keys[0])			
			# Right pointer
			if avb_node.right.keys[0].value < self.keys[0].value:
				# If no left connection exists, create it
				if self.left == None:
					self.left = AvbNode(avb_node = avb_node.right, parent = self)
				else:
					self.left.add_key_to_node(avb_node.right.keys[0])
			elif avb_node.right.keys[0].value > self.keys[0].value and avb_node.right.keys[0].value < self.keys[1].value:
				# If no middle connection exists, create it
				if self.middle == None:
					self.middle = AvbNode(avb_node = avb_node.right, parent = self)
				else:
					self.middle.add_key_to_node(avb_node.right.keys[0])
			else:
				# If no right connection exists, create it
				if self.right == None:
					self.right = AvbNode(avb_node = avb_node.right, parent = self)
				else:
					self.right.add_key_to_node(avb_node.right.keys[0])

		# Behavior if node now has more than 2 keys
		elif len(self.keys) > 2:
			# New left and right childs for this nodes
			L = AvbNode(node = self.keys[0], parent = self)
			R = AvbNode(node = self.keys[2], parent = self)
			# The new value is the smallest key value, so it came from the left side of the tree
			if self.keys[0] == avb_node.keys[0]:
				L.left = avb_node.left
				L.right = avb_node.right
				R.left = self.middle
				R.right = self.right
			# The new value is the middle key value, so it came from the middle of the tree
			elif self.keys[1] == avb_node.keys[0]:
				L.left = self.left
				L.right = avb_node.left
				R.left = avb_node.right
				R.right = self.right
			# The new value is the largest key value, so it came from the right side of the tree
			elif self.keys[2] == avb_node.keys[0]:
				L.left = self.left
				L.right = self.middle
				R.left = avb_node.left
				R.right = avb_node.right
			# Remove the values now that they are linked
			del self.keys[2]
			del self.keys[0]
			self.middle = None
			self.left = L
			self.right = R
			L.left.parent = L
			L.right.parent = L
			R.left.parent = R
			R.right.parent = R
			# Call recursively on parent if one exists, otherwise this is the root
			if self.parent != None:
				self.remove_self_from_parent()
				self.parent.node_handler(self)

	def add_to_dotGraph(self, dotGraph):
		# Add children of this AvbNode to the dotGraph if they exist
		if self.left != None:
			dotGraph.node(self.left.uniqueID, self.left.value_string())
			dotGraph.edge(self.uniqueID, self.left.uniqueID)
			self.left.add_to_dotGraph(dotGraph)
		if self.middle != None:
			dotGraph.node(self.middle.uniqueID, self.middle.value_string())
			dotGraph.edge(self.uniqueID, self.middle.uniqueID)
			self.middle.add_to_dotGraph(dotGraph)
		if self.right != None:
			dotGraph.node(self.right.uniqueID, self.right.value_string())
			dotGraph.edge(self.uniqueID, self.right.uniqueID)
			self.right.add_to_dotGraph(dotGraph)
		# Connect this AvbNode to the samples it represents
		for key in range(len(self.keys)):
			for sample in range(self.keys[key].nr_samples):
				dotGraph.edge(self.uniqueID, self.keys[key].samples[sample].uniqueID)
