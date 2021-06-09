import csv
from math import sqrt
import os

import pandas as pd
import numpy as np

from PIL import Image

from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor


# Number of neighbors (tests resulted in 5 having the lowest error)
neighbors = 5

columns = ['x', 'y', 'm', 'score']


render_scale = 4

renders_path = os.path.join(os.path.abspath(os.getcwd()), 'renders')

# reading data
data_path = os.path.join(os.path.abspath(os.getcwd()), 'output')
data = pd.read_csv(os.path.join(data_path, 'X[-1.5, 1.5]__Y[1.5, -1.5]__M[3e+27]__N[1442401].csv'), names=columns, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

# extracting used parameters
T = [data['x'].min(), data['x'].max(), data['y'].max(), data['y'].min()]
M = data['m'].unique()
N = data.shape[0]
resolution_per_axis = int( sqrt(N / len(M)) * render_scale )

# constructing new data with better reolution
X = np.linspace(T[0], T[2], resolution_per_axis)
Y = np.linspace(T[1], T[3], resolution_per_axis)
args = []


# removing mass from everything if only one is present
if len(M) == 1:
    columns.remove('m')
    data.drop(columns=['m'], inplace=True)
    args = [[x, y] for y in Y for x in X]
else:
    args = [[x, y, m] for m in M for y in Y for x in X]

del X, Y

# Splitting into training and test data
X = data[columns[:-1]].to_numpy()
y = data[columns[-1]].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.33)

knn = KNeighborsRegressor(n_neighbors=neighbors, weights='distance', n_jobs=-1)
knn.fit(X_train, y_train)

y_pred = knn.predict(X_test)
print('Mean squared error: ' + str(mean_squared_error(y_test,y_pred)))


pred_data = np.array(knn.predict(args))

pred_data.resize((resolution_per_axis, resolution_per_axis))
im = Image.fromarray(np.uint8(np.interp(pred_data, [0, 1], [0, 255])))
im.save(os.path.join(renders_path, f'N{N}_R{render_scale}.png'))

print('Exported predicted image to: ' + os.path.join(renders_path, f'N{N}_R{render_scale}.png'))