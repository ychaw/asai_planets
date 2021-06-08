import os
import csv

import pandas as pd
import numpy as np

from sklearn.neighbors import KNeighborsRegressor
from sklearn.utils import shuffle

# Amount of data used for training the knn
training_percent = 80

# Number of neighbors (tests resulted in 5 having the lowest error)
neighbors = 5

columns = ['x', 'y', 'm', 'score']


# reading data
data_path = os.path.join(os.path.abspath(os.getcwd()), 'output')
data = pd.read_csv(os.path.join(data_path, 'X[-1.5, 1.5]__Y[1.5, -1.5]__M[3e+27]__N[1442401].csv'), names=columns, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

# removing mass from everything if only one is present
if len(data['m'].unique()) == 1:
    columns.remove('m')
    data.drop(columns=['m'], inplace=True)

# Shuffling of the data so that the division into training and test data does not distort the result
data = shuffle(data).reset_index(drop=True)

# Splitting into training and test data
train = data[:int(len(data)*(training_percent/100))].reset_index(drop=True)
test = data[int(len(data)*(training_percent/100)):].reset_index(drop=True)

X_train = train[columns[:-1]]
y_train = train[columns[-1]]

X_test = test[columns[:-1]]
y_test = test[columns[-1]]

knn = KNeighborsRegressor(n_neighbors=neighbors, weights='distance', n_jobs=-1)
knn.fit(X_train, y_train)

test_predicted = X_test.join(pd.DataFrame(knn.predict(X_test), columns=['pred_score'])).join(y_test)
test_predicted['error'] = test_predicted.apply(lambda row: abs(row['pred_score'] - row['score']), axis=1)

error = test_predicted['error'].mean()

print(test_predicted)

print(error)
