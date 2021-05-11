import pygame
import math
import sys
import os
import datetime
from astroquery.jplhorizons import Horizons
from astropy.time import Time

from orbitalsim.environment import OrbitalSystem


class Simulation():
    def __init__(
        self,
        dimensions=(800, 800),
        scale=-1,
        entity_scale=10,
        start_date=None,
        fullscreen=False
    ):
        # dimensions: (width, height) of the window in pixels
        # scale: magnification ratio between AU and displayed pixels (default of -1: automatically calculated by self.set_scale())
        # entity_scale: additional magnification on the entities for visibility purposes
        # fullscreen: boolean – if true, automatically overrides dimensions
        self.width, self.height = dimensions

        # dx, dy: offset in px as a result of panning with arrow keys
        # offsetx, offsety: constants to centre (0,0) in the window
        self.dx = 0
        self.dy = 0
        self.offsetx = self.width / 2
        self.offsety = self.height / 2

        self.default_scale = scale
        self.scale = scale
        self.entity_scale = entity_scale

        if start_date:
            self.date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        else:
            self.date = datetime.datetime.today()

        # initialise the Orbital System object
        self.solar_system = OrbitalSystem()

        self.fullscreen = fullscreen
        self.show_labels = True
        self.show_history = True
        self.running = False
        self.paused = True

        self.histories = []

    """ 
    Viewmodel control
    """

    def scroll(self, dx=0, dy=0):
        # change offset to scroll/pan around the screen
        relative_scale = self.scale / self.default_scale
        self.dx += dx / relative_scale
        self.dy += dy / relative_scale

    def zoom(self, zoom):
        # adjust zoom level and zoom offset
        self.scale *= zoom

    def reset_zoom(self):
        # reset all viewmodel variables to default
        self.scale = self.default_scale
        self.dx = 0
        self.dy = 0

    def set_scale(self, max_a):
        # automatically calculate and set the scale based on the largest semi-major axis in the array of entities;
        # does nothing if scale manually set
        if self.scale < 0:
            new_scale = min(self.width, self.height) / (2 * max_a)
            self.scale = new_scale
            self.default_scale = new_scale

    """
    Adding entities to simulation
    """

    def add_custom_entity(
        self,
        position,
        mass,
        speed=0,
        angle=0,
        diameter=1e-5,
        e=0,
        a=None,
        name='',
        color=(255, 255, 255),
    ):
        # position: tuple (x, y) describing the distance in AU from the centre of the system (0, 0)
        # speed: magnitude of initial velocity measured in AU/day
        # angle: angle of initial velocity given in rad
        # mass: measured in kg
        # diameter: measured in AU
        # (if applicable) e: eccentricity of the entity's orbit ranging from 0-1
        # (if applicable) a: semi-major axis of the entity's orbit measured in AU
        # (if applicable) name: str to display next to the entity when labels turned on
        if not a:
            x, y = position
            a = math.hypot(x, y)

        self.solar_system.add_entity(
            position=position,
            speed=speed,
            angle=angle,
            mass=mass,
            diameter=diameter,
            e=e,
            a=a,
            name=name,
            color=color
        )

    """
    Simulation functions
    """

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # pause simulation using spacebar
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.key == pygame.K_LEFT:
                self.scroll(dx=30)
            elif event.key == pygame.K_RIGHT:
                self.scroll(dx=-30)
            elif event.key == pygame.K_UP:
                self.scroll(dy=30)
            elif event.key == pygame.K_DOWN:
                self.scroll(dy=-30)
            elif event.key == pygame.K_MINUS:
                self.zoom(0.667)
            elif event.key == pygame.K_EQUALS:
                self.zoom(1.5)
            elif event.key == pygame.K_r:
                self.reset_zoom()
            elif event.key == pygame.K_PERIOD:
                self.change_sim_rate(2)
            elif event.key == pygame.K_COMMA:
                self.change_sim_rate(0.5)
            elif event.key == pygame.K_l:
                self.show_labels = not self.show_labels
            elif event.key == pygame.K_h:
                self.show_history = not self.show_history
                self.histories = [[] for _ in range(len(self.solar_system.entities))]
            elif event.key == pygame.K_q:
                self.running = False
                pygame.quit()
                sys.exit()

    """
    Main simulation function
    """

    def start(self):
        """ 
        Setup 
        """
        pygame.init()

        if self.fullscreen:
            flag = pygame.FULLSCREEN

            display_info = pygame.display.Info()
            self.width = display_info.current_w
            self.height = display_info.current_h
            self.offsetx = self.width / 2
            self.offsety = self.height / 2
        else:
            flag = 0
        self.window = pygame.display.set_mode((self.width, self.height), flag)
        pygame.display.set_caption('Orbital Simulation')
        delta_t = 16

        # calculate the largest semi-major axis and calculates scale if applicable
        semimajor_axes = []
        for entity in self.solar_system.entities:
            self.histories.append([])
            semimajor_axes.append(entity.a)
        self.set_scale(max(semimajor_axes) + 0.2)

        font_dir = '{}/fonts/Inconsolata.ttf'.format(os.path.dirname(__file__))
        font = pygame.font.Font(font_dir, 14)
        clock = pygame.time.Clock()
        self.running = True

        """
        Simulation loop
        """
        while self.running:
            # handle events
            for event in pygame.event.get():
                self.handle_event(event)

            # update frame
            if not self.paused:
                self.solar_system.update()

            # render frame
            self.window.fill(self.solar_system.bg)

            if self.show_history:
                for i, ent_history in enumerate(self.histories):
                    for hist in ent_history[1:]:
                        pygame.draw.line(self.window, self.solar_system.entities[i].color, hist, ent_history[ent_history.index(hist)-1])

            entity_labels = []
            for i, entity in enumerate(self.solar_system.entities):
                # calculate pygame x, y coords
                # this zooming stuff/scale is super sketchy yikes
                relative_scale = self.scale / self.default_scale
                x = int(relative_scale * ((self.scale * entity.x) + self.dx) + self.offsetx)
                # reflected across y-axis to compensate for pygame's reversed axes
                y = int(relative_scale * ((self.scale * -entity.y) + self.dy) + self.offsety)
                r = abs(int(entity.diameter * self.scale * self.entity_scale / 2)) * 2

                if r < 6:
                    r = 6

                pygame.draw.circle(self.window, entity.color, (x, y), r, 0)

                label = font.render(entity.name, False, (180, 180, 180))
                entity_labels.append((label, (x + 3 + r, y + 3 + r)))

                if self.show_history and not self.paused:
                    self.histories[i].append((x, y))
                    if len(self.histories[i]) > entity.a * 400:
                        self.histories[i] = self.histories[i][1:]

            if self.show_labels:
                for label in entity_labels:
                    text, position = label
                    self.window.blit(text, position)

            pygame.display.flip()

            # delta_t hat zwar in der Simulation keine Auswirkung (mehr), ist aber gut für die Visualisierung
            delta_t = clock.tick(60)
