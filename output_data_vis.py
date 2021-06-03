import os
import sys
from math import sqrt, log
import colorsys

import pygame
import csv

import pandas as pd
from numpy import interp


class Visualization():
    def __init__(self, filename, selected_mass=0, zoom=1):

        self.zoom = zoom
        self.running = True

        self.data_path = os.path.join(os.path.abspath(os.getcwd()), 'output')
        self.data = pd.read_csv(os.path.join(self.data_path, filename), names=['x', 'y', 'm', 'score'], delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        self.data = self.data[self.data['m'] == list(set(self.data['m']))[selected_mass]]

        self.width = int(sqrt(self.data.shape[0])) * self.zoom
        self.height = self.width

        print(self.width, self.height)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            pygame.quit()
            sys.exit()

    def draw(self):
        # render frame
        self.window.fill((0, 0, 0))

        for i in range(self.data.shape[0]):

            # normal linear scale
            score = self.data.iat[i, 3]

            # lerping to a logarithmic scale
            # score = log((self.data.iat[i, 3]+1), 2)

            # Black and white
            c = [interp(score, [0, 1], [0, 255]) for _ in range(3)]

            # HSV color spectrum
            # c = [interp(cc, [0,1], [0,255]) for cc in colorsys.hsv_to_rgb(score, 0.6, 1)]

            x = (i * self.zoom) % self.width
            y = (i * self.zoom) // self.height * self.zoom

            pygame.draw.rect(self.window, c, pygame.Rect(x, y, self.zoom, self.zoom))

        pygame.display.flip()

    def start(self):
        pygame.init()

        self.window = pygame.display.set_mode((self.width, self.height), 0)
        pygame.display.set_caption('Data Visualization')

        self.draw()
        print('finished drawing')

        while self.running:
            # handle events
            for event in pygame.event.get():
                self.handle_event(event)


if __name__ == '__main__':
    v = Visualization(filename='X[-1.5, 1.5]__Y[1.5, -1.5]__M[3e+27]__N[1442401].csv')
    v.start()
