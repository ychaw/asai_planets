import os
from math import sqrt

import csv

import pandas as pd
import numpy as np

from PIL import Image


selected_file = 3


renders_path = os.path.join(os.path.abspath(os.getcwd()), 'renders', 'simulation_data')

data_path = os.path.join(os.path.abspath(os.getcwd()), 'output')
filename = os.listdir(data_path)[selected_file]
print('reading:' + filename)
data = pd.read_csv(os.path.join(data_path, filename), names=['x', 'y', 'm', 'score'], delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

N = data.shape[0]
masses = data['m'].unique()

resolution_per_axis = int(sqrt(N / len(masses)))

for i, mass in enumerate(masses):

    filtered_data = data[data['m'] == mass].copy()

    filtered_data.sort_values(by=['y', 'x'], ascending=[False, True], inplace=True)
    scores = np.array(filtered_data['score'])

    scores.resize((resolution_per_axis, resolution_per_axis))
    im = Image.fromarray(np.uint8(np.interp(scores, [0, 1], [0, 255])))

    splitted_filename = filename[:-4].split('__')
    new_mass = splitted_filename[2][2:-1].split(', ')[i]
    new_filename = f'{splitted_filename[0]}__{splitted_filename[1]}__M[{new_mass}]__{splitted_filename[3]}.png'
    im.save(os.path.join(renders_path, new_filename))
    print('saved to:' + new_filename)