import os
import sys
from math import sqrt

import pygame
import csv

import pandas as pd
from numpy import interp


class Visualization():
    def __init__(self, dimensions=(800, 800), filename='-0.4_1.1-0.4_0.3-N19683.csv', selected_mass=0, pixel_perfect=True, zoom=1):

        self.width, self.height = dimensions
        self.zoom = zoom
        self.running = True

        self.data_path = os.path.join(os.path.abspath(os.getcwd()), 'output')
        self.data = pd.read_csv(os.path.join(self.data_path, filename), names=['x', 'y', 'm', 'score'], delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        if pixel_perfect:
            self.width = int(sqrt(self.data.shape[0])) * self.zoom
            self.height = self.width

        print(self.width, self.height)

        self.data = self.data[self.data['m'] == list(set(self.data['m']))[selected_mass]]

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            pygame.quit()
            sys.exit()

    def draw(self):
        # render frame
        self.window.fill((0, 0, 0))

        for i in range(self.data.shape[0]):
            shade = interp(self.data.iat[i, 3], [0, 1], [0, 255])
            c = (shade, shade, shade)

            x = (i * self.zoom // self.height) * self.zoom
            y = self.height - (i * self.zoom) % (self.height)

            pygame.draw.rect(self.window, c, pygame.Rect(x, y-self.zoom, self.zoom, self.zoom))

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
    v = Visualization(filename='-1.5_1.5-1.5_-1.5-N1442401.csv')
    v.start()
