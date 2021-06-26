import csv
import math
import os
from math import sqrt
from random import choice

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor

from vis import start_visualization


def start_agent(neighbors, selected_file, scale):

    columns = ['x', 'y', 'm', 'score']

    data_path = os.path.join(os.path.abspath(os.getcwd()), 'output')
    filename = os.listdir(data_path)[selected_file]
    print('\nreading: ' + filename)

    # reading data
    data = pd.read_csv(os.path.join(data_path, filename), names=columns, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    # extracting used parameters
    T = [data['x'].min(), data['y'].max(), data['x'].max(), data['y'].min()]
    M = data['m'].unique()
    N = data.shape[0]
    resolution_per_axis = int(sqrt(N // len(M)) * scale)

    # constructing new data with better resolution
    X = np.linspace(T[0], T[2], resolution_per_axis)
    Y = np.linspace(T[1], T[3], resolution_per_axis)
    args = [[x, y, m] for m in M for y in Y for x in X]
    del X, Y

    # Splitting into training and test data
    X = data[columns[:-1]].to_numpy()
    y = data[columns[-1]].to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)

    knr = KNeighborsRegressor(n_neighbors=neighbors, weights='distance', n_jobs=-1)

    knr.fit(X_train, y_train)
    y_pred = knr.predict(X_test)
    print('\nMean squared error: {}'.format(mean_squared_error(y_test, y_pred)))
    print('Score:              {}\n'.format(knr.score(X_test, y_test)))

    knr.fit(X, y)
    pred_data = list(knr.predict(args))

    scores = [(args[i], d) for i, d in enumerate(pred_data)]
    scores.sort(key=lambda x: x[1], reverse=True)

    return T, M, scores


if __name__ == '__main__':

    file = 0
    neighbours = 9
    scale = 4

    T, M, R = start_agent(neighbours, file, scale)

    # x1, y1, x2, y2 of simulation space
    sim_space = [T[0], T[1], T[2], T[3]]

    if R[0][1] > 0.9:
        best = choice(R[:[x[1] > 0.98 for x in R].index(False)])
    else:
        best = R[0]

    print(best)
    print()

    custom_entity = {
        'name': 'Custom',
        'color': (255, 0, 0),
        'position': tuple(best[0][:2]),
        'mass': best[0][-1],
        'speed': 0.015,
        'angle': math.atan2(best[0][:2][1], best[0][:2][0]) + math.pi,
        'score': best[1]
    }

    start_visualization(1000, sim_space, custom_entity)
