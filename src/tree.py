import classes
import dataParser
import numpy as np
from statistics import median
import time


def create_AGDS(filename):

	[data, columns] = dataParser.read_xls_iris(filename)

	nr_samples = data.shape[0]
	nr_attributes = data.shape[1]

	# Create objects
	samples = []
	for sample_nr in range(nr_samples):
		samples.append(classes.Sample(name = str(sample_nr), nodes = []))

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

	return classes.Tree(tree_type = 'AGDS', attributes = attributes, samples = samples)


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
	# Printing
	# for i in range(len(list_of_sample_similarity)): # Print all samples
	for i in range(10): # Print first 10 samples
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
	# Each line of data  = [table name, column names, columns of data]
	[data, primary_keys_array] = dataParser.read_db(filename)

	# Flattening primary_keys_array for use in detection of both primary and foreign keys
	primary_keys = []
	for table_pk in primary_keys_array:
		for pk in table_pk:
			primary_keys.append(pk)

	# Create sample objects
	samples = []
	for pk in primary_keys:
		# samples store [primary key name, list of existings values, corresponding sample objects] 
		samples.append([pk, [], []])
	# For each table
	for table in data:
		# Columns in table (table[1] is column names)
		for column in range(len(table[1])):
			# For all primary keys
			for pk in range(len(primary_keys)):
				# Check if the <col> name matches the primary key
				if table[1][column] == primary_keys[pk]:
					# Iterate over the rows in this <column>
					for item in table[2][column]:
						# Check whether the <item> already exists in the list of sample objects
						if not (set(samples[pk][1]) & set([item])):
							# Add the <item>
							samples[pk][1].append(item)
							samples[pk][2].append(classes.Sample(name = "{0}: {1}".format(samples[pk][0], item), nodes = [], foreign_samples = []))
	# For tables with multiple keys (primary or foreign) the sample objects get linked
	for table_nr in range(len(data)):
		if len(set(primary_keys) & set(data[table_nr][1])) > len(primary_keys_array[table_nr]):
			# Getting the primary and foreign keys in this table
			pk = primary_keys_array[table_nr]
			keys_in_table = set(primary_keys) & set(data[table_nr][1])
			fk = list(keys_in_table.difference(set(primary_keys_array[table_nr])))
			pk_col_t = []
			pk_col_s = []
			fk_col_t = []
			fk_col_s = []
			# Finding the columns in <samples> that correspond to this table's primary keys
			for p in pk:
				pk_col_t.append(data[table_nr][1].index(p))
				for s in range(len(samples)):
					if samples[s][0] == p:
						pk_col_s.append(s)
			# Finding the columns in <samples> that correspond to this table's foreign keys
			for f in fk:
				fk_col_t.append(data[table_nr][1].index(f))
				for s in range(len(samples)):
					if samples[s][0] == f:
						fk_col_s.append(s)
			# Connecting the sample objects
			for row_nr in range(len(data[table_nr][2][0])):
				for p in range(len(pk_col_t)):
					pk_row_s = samples[pk_col_s[p]][1].index(data[table_nr][2][pk_col_t[p]][row_nr])
					for f in range(len(fk_col_t)):
						fk_row_s = samples[fk_col_s[f]][1].index(data[table_nr][2][fk_col_t[f]][row_nr])
						samples[pk_col_s[p]][2][pk_row_s].foreign_samples.append(samples[fk_col_s[f]][2][fk_row_s])
						samples[fk_col_s[f]][2][fk_row_s].add_foreign_samples(samples[pk_col_s[p]][2][pk_row_s])

	# Create attributes
	attributes = []
	table_nr = 0
	# For each table
	for table in data:
		# Get keys present in this table
		pk = list(set(primary_keys_array[table_nr]) & set(table[1]))
		table_nr += 1
		table_columns_with_pk = []
		samples_columns_with_pk = []
		for key in pk:
			# Find the columns which contain those keys in <table>
			for i in range(len(table[1])):
				if table[1][i] == key:
					table_columns_with_pk.append(i)
			# Find the columns which contain those keys in <samples>
			for i in range(len(samples)):
				if samples[i][0] == key:
					samples_columns_with_pk.append(i)

		# Creating a list of columns of nodes (list of list) and a list of columns indexes which aren't keys
		node_columns = []
		columns_without_keys = []
		for column in range(len(table[1])):
			if not (set(primary_keys) & set([table[1][column]])):
				node_columns.append([])
				columns_without_keys.append(column)

		# Rows of data in the table
		for row in range(len(table[2][0])):
			# Getting sample objects for this row
			row_samples = []
			# This adds samples corresponding to all primary keys in the row
			for i in range(len(table_columns_with_pk)):
				# Find the sample with a value matching that of the pk value in column pointed to at <i> in this <row>
				# tmp = np.where(samples[samples_columns_with_pk[i]][1] == table[2][table_columns_with_pk[i]][row])[0][0]
				tmp = samples[samples_columns_with_pk[i]][1].index(table[2][table_columns_with_pk[i]][row])

				row_samples.append(samples[samples_columns_with_pk[i]][2][tmp])

			# Columns in this row
			col_index = 0
			for column in columns_without_keys:
				# New node for the row
				node_columns[col_index].append(classes.Node(attribute = None, value = table[2][column][row], samples = row_samples))
				for sample in row_samples:
					# Adding the node to the sample object
					sample.add_nodes(node_columns[col_index][-1])
				col_index += 1
		
		# Adding new attributes
		col_index = 0
		for column in columns_without_keys:
			attributes.append(classes.Attribute(name = table[1][column], nodes = node_columns[col_index]))
			# Attach the new attributes to their nodes
			for i in range(len(node_columns[col_index])):
				node_columns[col_index][i].attribute = attributes[-1]
			col_index += 1
					
	for sample in samples:
		del sample[1]

	DASNG = classes.Tree(tree_type = 'DASNG', attributes = attributes, samples = samples)

	return DASNG
