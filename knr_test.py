import csv
from math import sqrt
import os

import pandas as pd
import numpy as np

from PIL import Image

from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor


def main(selected_file, neighbors, render, render_scale):

    columns = ['x', 'y', 'm', 'score']

    if render:
        renders_path = os.path.join(os.path.abspath(os.getcwd()), 'renders', 'prediction_data')

    data_path = os.path.join(os.path.abspath(os.getcwd()), 'output')
    filename = os.listdir(data_path)[selected_file]
    print('reading:' + filename)

    # reading data
    data = pd.read_csv(os.path.join(data_path, filename), names=columns, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    # extracting used parameters
    T = [data['x'].min(), data['y'].max(), data['x'].max(), data['y'].min()]
    M = data['m'].unique()
    N = data.shape[0]
    resolution_per_axis = int(sqrt(N // len(M)) * render_scale)

    if render:
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
    print('Mean squared error: ' + str(mean_squared_error(y_test, y_pred)))
    print('Score:              ' + str(knr.score(X_test, y_test)))

    if render:
        pred_data = np.array(knr.predict(args))

        for i, split_pred_data in enumerate([pred_data[i:i + len(pred_data) // len(M)] for i in range(0, len(pred_data), len(pred_data) // len(M))]):

            split_pred_data.resize((resolution_per_axis, resolution_per_axis))

            im = Image.fromarray(np.uint8(np.interp(split_pred_data, [0, 1], [0, 255])))

            splitted_filename = filename[:-4].split('__')
            new_mass = splitted_filename[2][2:-1].split(', ')[i]
            new_filename = f'R{render_scale}__{splitted_filename[0]}__{splitted_filename[1]}__M[{new_mass}]__{splitted_filename[3]}.png'

            im.save(os.path.join(renders_path, new_filename))

            print('Exported predicted image to: ' + os.path.join(renders_path, new_filename))


if __name__ == '__main__':

    selected_file = 0

    neighbors = 9
    render_image = False
    render_scale = 4

    main(selected_file, neighbors, render_image, render_scale)
