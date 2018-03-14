# import MySQLdb

# db = MySQLdb.connect(
#     host='localhost',
#     user='root',
#     passwd='1',
#     db='positioning'
# )

# curs = db.cursor()
# curs.execute("SELECT * FROM accelerations LIMIT 10")
# response = curs.fetchall()
# for row in response:
#     print(row)

import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from scipy import integrate
from sklearn.externals import joblib


from activity_data import parseTraces

vecs = []
labels = []

ats, a = parseTraces.getAccMagn(os.path.join('activity_data/data', 'p1.1_Female_20-29_170-179cm_Hand_held.out'))
plt.plot(ats, a, '.-')
plt.xlabel('timestamp(s)')
plt.ylabel('acceleration(m/s^2)')
plt.show()

def extract_feature(filename, startWalking, endWalking):
	ats, a = parseTraces.getAccMagn(os.path.join('activity_data/data', filename))

	windowSize = 200
	vecs = []
	labels = []

	for i in range(0, len(a) - windowSize, windowSize / 2):
		window = a[i:i+windowSize]
		vecs.append([np.median(window), np.mean(window), np.min(window), np.max(window), np.std(window)])
		# integrate.simps(window, ats[i:i+windowSize])
		if i + windowSize < startWalking or i > endWalking:
			labels.append(0)
		else:
			labels.append(1)
	print(vecs)
	return vecs, labels

groundtruthWD = []
with open(os.path.join('activity_data', 'groundtruth_WD.txt'), 'r') as f:
	for line in f.readlines():
		d = line.split()
		filename = d[0].split('.')
		pid = ''
		place = ''
		if len(filename) > 1:
			pid = filename[0] + '.' + filename[1][0]
			place = filename[1][1:]
		if len(d) > 2:
			groundtruthWD.append([pid, place, d[1][1:], d[2][0:-1]])

# print(groundtruthWD)

# for filename in os.listdir("activity_data/data"):
# 	if filename.rpartition('.')[2]=='dat' or filename.rpartition('.')[2]=='out':
# 		a = [x for x in groundtruthWD if x[0] != '' and filename.find(x[0]) != -1 and filename.find(x[1]) != -1]
# 		if len(a) > 0 and len(a[0]) > 3:
# 			[[_, _, startWalking, endWalking]] = a
#         	vec, label = extract_feature(filename, int(startWalking), int(endWalking))
#         	vecs.extend(vec)
#         	labels.extend(label)

# print(len(vecs))
# print(len(labels))

# print(labels)
# print(vecs)

X_train, X_test, y_train, y_test = train_test_split(vecs, labels, test_size=0.2, random_state=42)
filenameModelSave = 'model_svm.sav'

def predict_svm(x,y,x_test,y_test):
    linear_svc = svm.SVC(kernel='rbf')
    linear_svc.fit(x, y)
    result = linear_svc.predict(x_test)
    joblib.dump(linear_svc, filenameModelSave)
    print ( accuracy_score(y_test, result))

# predict_svm(X_train, y_train,X_test,y_test)


