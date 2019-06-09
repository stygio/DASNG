import pandas as pd
import numpy as np
import sqlite3


# Returns data and column names from given .xls files
def read_xls_iris(filename):
	raw_data = pd.read_excel(filename)
	colNames = raw_data.columns

	data = np.array(raw_data)	
	return [data, colNames]


# Returns data from the requested database in the following format:
# [table_name[table 0], column_names[table 0], column_data[table 0]]
# [table_name[table 1], column_names[table 1], column_data[table 1]]
# [table_name[table 2], column_names[table 2], column_data[table 2]]
# ...etc
def read_db(filename):
	# Establish connection to request database
	db_connection = sqlite3.connect(filename)
	db = db_connection.cursor()
	# Get table names
	tables = db.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
	tableInfo = []

	tmpInfo = []
	for table_name in tables:
		# Get formated table names (they are returned as tuples)
		table_name = table_name[0]
		if table_name != "sqlite_sequence":
			# Store table names in tableInfo
			tableInfo.append(table_name)
			# Get schema information for each table
			tmpInfo.append(db.execute("PRAGMA table_info('{0}')".format(table_name)).fetchall())

	for i in range(len(tmpInfo)):
		columnNames = []
		columnData = []
		for j in range(len(tmpInfo[i])):
			# Extract column names
			columnNames.append(tmpInfo[i][j][1])
		for column_name in columnNames:
			# Extract column data
			line = db.execute("SELECT {0} FROM {1}".format(column_name, tableInfo[i])).fetchall()
			for k in range(len(line)):
				line[k] = line[k][0]
			columnData.append(line)
		# For each table [i] add information about its name, column names and the data in each of those columns
		tableInfo[i] = [tableInfo[i], columnNames, columnData]

	return tableInfo