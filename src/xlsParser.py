import pandas as pd
import numpy as np

def read_xls_iris(filename):
	raw_data = pd.read_excel(filename)
	colNames = raw_data.columns

	data = np.array(raw_data)	
	return [data, colNames]


# def read_xls(filename, shuffle=1):

# 	if 'Iris' in filename:
# 		[data, colNames] = read_xls_iris(filename, shuffle)

# 	else:
# 		raw_data = pd.read_excel(filename)
# 		colNames = raw_data.columns

# 		data = np.array(raw_data)
# 		if shuffle:
# 			np.random.shuffle(data[2:,:])

# 		classCol = np.where(data=="CLASS")[1][0]
# 		tmpOut = data[2:, classCol]
# 		tmpIn = np.delete(data, classCol, 1)
# 		# Checking each column for string data
# 		for i in range(np.shape(tmpIn)[1]):
# 			if tmpIn[1][i] == "string":
# 				values = np.unique(tmpIn[2:, i].astype(str))
# 				for j in range(len(values)):
# 					for k in range(len(tmpIn[2:, i])):
# 						if tmpIn[2+k, i] == values[j]:
# 							tmpIn[2+k, i] = j
# 		inputs = tmpIn[2:, :].astype(float)
		
# 		categories = np.unique(tmpOut)
# 		outputs = []
# 		for i in range(len(tmpOut)):
# 			row = []
# 			#print("tmpOut[{0}] = {1}".format(i, tmpOut[i]))
# 			for j in range(len(categories)):
# 				#print(categories[j])
# 				if tmpOut[i] == categories[j]:
# 					row.append(1)
# 				else:
# 					row.append(0)
# 			outputs.append(row)
# 		outputs = np.array(outputs)
# 		categories = categories.astype(str)
	
# 	return [inputs, outputs, categories, colNames]