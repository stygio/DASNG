import classes
import dataParser
import numpy as np
from statistics import median
import time


def create_tree(filename):

	[data, columns] = dataParser.read_xls_iris(filename)

	nr_samples = data.shape[0]
	nr_attributes = data.shape[1]

	# Create objects
	samples = []
	for sample_nr in range(nr_samples):
		samples.append(classes.Sample(number = sample_nr, nodes = []))

	# Create attributes and nodes
	attributes = []
	for category in range(nr_attributes):
		nodes = []
		unique_values = np.unique(data[:, category])
		for node in range(len(unique_values)):
			# New node
			nodes.append(classes.Node(attribute = None, value = unique_values[node], samples = []))
			# Indexes of objects whose value matches this node
			sample_indexes = np.where(data[:, category] == unique_values[node])[0]
			for sample in range(len(sample_indexes)):
				# Adding the objects to the node
				nodes[-1].add_objects(samples[sample_indexes[sample]])
				# Adding the node to the object
				samples[sample_indexes[sample]].add_nodes(nodes[-1])
		# New attribute
		attributes.append(classes.Attribute(name = columns[category], nodes = nodes))
		for i in range(len(nodes)):
			nodes[i].attribute = attributes[-1]

	return classes.Tree(attributes = attributes, samples = samples)


def calculate_similarities(AGDS, tmpSample = None, tmpValues = []):
	list_of_sample_similarity = []
	for i in range(len(AGDS.samples)):
		AGDS.samples[i].calculate_similarity(sample = tmpSample, values = tmpValues)
		list_of_sample_similarity.append([AGDS.samples[i], AGDS.samples[i].similarity])
	# Sorting
	list_of_sample_similarity = np.array(list_of_sample_similarity)
	sorted_indexes = np.argsort(list_of_sample_similarity[:, 1], axis=0)
	list_of_sample_similarity = list_of_sample_similarity[sorted_indexes]
	list_of_sample_similarity = list_of_sample_similarity[::-1]	# Descending order
	for i in range(len(list_of_sample_similarity)):
		print("{0}; Similarity = {1:.2f}%".format(list_of_sample_similarity[i][0].value_string(), list_of_sample_similarity[i][1]*100))
	return list_of_sample_similarity


def sort_by_similarity(AGDS):
	print("Sort the objects existing in the AGDS by their similarity to the chosen sample or values.")
	choice = input("Would you like to choose a sample or enter values? (Enter [Sample] or [Values] - case sensitive): ")
	if choice == "Sample":
		sample_choice = None
		is_sample_chosen = 'N'
		while is_sample_chosen != 'Y':
			sample_choice = int(input("Choose a sample in range {0} - {1}: ".format(0, len(AGDS.samples)-1)))
			print("Chosen sample = {0}".format(AGDS.samples[sample_choice].value_string()))
			is_sample_chosen = input("Is this your choice? (Enter [Y] or [N] - case sensitive): ")
		return calculate_similarities(AGDS, tmpSample = AGDS.samples[sample_choice])

	elif choice == "Values":
		valueList = []
		for i in range(len(AGDS.attributes)):
			if type(AGDS.attributes[i].avb_tree.root.keys[0].value) == str:
				valueList.append(str(input("Enter {0}: ".format(AGDS.attributes[i].name))))
			else:
				valueList.append(float(input("Enter {0}: ".format(AGDS.attributes[i].name))))
		return calculate_similarities(AGDS, tmpValues = valueList)

	else:
		print("Invalid choice.")


def median_benchmark(AGDS, data):
	print("-> Python library - statistics.median")
	for i in range(len(AGDS.attributes)):
		if type(AGDS.attributes[i].avb_tree.root.keys[0].value) != str:
			tmpTime = time.time()
			tmpMedian = median(data[:, i])
			tmpTime = time.time() - tmpTime
			print("{0}: {1}, time: {2}".format(AGDS.attributes[i].name, tmpMedian, tmpTime))

	print("-> My getMedian() method")
	for i in range(len(AGDS.attributes)):
		if type(AGDS.attributes[i].avb_tree.root.keys[0].value) != str:
			tmpTime = time.time()
			tmpMedian = AGDS.attributes[i].getMedian()
			tmpTime = time.time() - tmpTime
			print("{0}: {1}, time: {2}".format(AGDS.attributes[i].name, tmpMedian, tmpTime))


def average_benchmark(AGDS, data):
	print("-> sum(data)/len(data)")
	for i in range(len(AGDS.attributes)):
		if type(AGDS.attributes[i].avb_tree.root.keys[0].value) != str:
			tmpTime = time.time()
			tmpAverage = sum(data[:, i])/len(data[:, i])
			tmpTime = time.time() - tmpTime
			print("{0}: {1}, time: {2}".format(AGDS.attributes[i].name, tmpAverage, tmpTime))

	print("-> My calculateAverage() method")
	for i in range(len(AGDS.attributes)):
		if type(AGDS.attributes[i].avb_tree.root.keys[0].value) != str: 
			tmpTime = time.time()
			tmpAverage = AGDS.attributes[i].calculateAverage()
			tmpTime = time.time() - tmpTime
			print("{0}: {1}, time: {2}".format(AGDS.attributes[i].name, tmpAverage, tmpTime))


def create_DASNG(filename):
	return 0
