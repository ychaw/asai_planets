import os
from math import sqrt

import csv

import pandas as pd
import numpy as np

from PIL import Image


filename = 'X[-1.5, 1.5]__Y[1.5, -1.5]__M[3e+27]__N[1442401].csv'
selected_mass = 0


renders_path = os.path.join(os.path.abspath(os.getcwd()), 'renders')

data_path = os.path.join(os.path.abspath(os.getcwd()), 'output')
data = pd.read_csv(os.path.join(data_path, filename), names=['x', 'y', 'm', 'score'], delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

N = data.shape[0]
resolution_per_axis = int(sqrt(N))

mass = list(sorted(set(data['m'])))[selected_mass]
data = data[data['m'] == mass]

data.sort_values(by=['y', 'x'], ascending=[False, True], inplace=True)
scores = np.array(data['score'])

scores.resize((resolution_per_axis, resolution_per_axis))
im = Image.fromarray(np.uint8(np.interp(scores, [0, 1], [0, 255])))
im.save(os.path.join(renders_path, f'N{N}.png'))
