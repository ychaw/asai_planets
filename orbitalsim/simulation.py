import math
import os
import sys

import pygame

from orbitalsim.environment import OrbitalSystem


class Simulation():
    def __init__(
        self,
        dimensions=(800, 800),
        scale=-1,
        entity_scale=10,
        fullscreen=False,
        max_runs=1000,
        sim_space=None,
        custom_entity=None
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

        # initialise the Orbital System object
        self.solar_system = OrbitalSystem()

        self.fullscreen = fullscreen
        self.show_labels = True
        self.show_history = True
        self.show_sim_space = False
        self.running = False
        self.paused = True
        self.max_runs = max_runs

        self.sim_space = sim_space
        self.custom_entity = custom_entity

        self.histories = []

    """ 
    Viewmodel control
    """

    def scroll(self, dx=0, dy=0):
        # change offset to scroll/pan around the screen
        relative_scale = self.scale / self.default_scale
        self.dx += dx / relative_scale
        self.dy += dy / relative_scale
        self.clear_history()

    def zoom(self, zoom):
        # adjust zoom level and zoom offset
        self.scale *= zoom
        self.clear_history()

    def reset_zoom(self):
        # reset all viewmodel variables to default
        self.scale = self.default_scale
        self.dx = 0
        self.dy = 0
        self.clear_history()

    def set_scale(self, max_a):
        # automatically calculate and set the scale based on the largest semi-major axis in the array of entities;
        # does nothing if scale manually set
        if self.scale < 0:
            new_scale = min(self.width, self.height) / (2 * max_a)
            self.scale = new_scale
            self.default_scale = new_scale

    def clear_history(self):
        self.histories = [[] for _ in range(len(self.solar_system.entities))]

    """
    Adding entities to simulation
    """

    def add_custom_entity(
        self,
        position,
        mass,
        speed=0,
        angle=None,
        name='',
        color=(255, 255, 255),
    ):
        # position: tuple (x, y) describing the distance in AU from the centre of the system (0, 0)
        # speed: magnitude of initial velocity measured in AU/day
        # angle: angle of initial velocity given in rad
        # mass: measured in kg
        # (if applicable) name: str to display next to the entity when labels turned on

        # If the angle is None, calculate the angle perpendicular to the sun
        if not angle:
            angle = math.atan2(position[1], position[0]) + math.pi

        self.solar_system.add_entity(
            position=position,
            mass=mass,
            speed=speed,
            angle=angle,
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
                self.zoom(5/6)
            elif event.key == pygame.K_PLUS:
                self.zoom(1.2)
            elif event.key == pygame.K_r:
                self.reset_zoom()
            elif event.key == pygame.K_l:
                self.show_labels = not self.show_labels
            elif event.key == pygame.K_h:
                self.show_history = not self.show_history
                self.clear_history()
            elif event.key == pygame.K_t:
                self.show_sim_space = not self.show_sim_space
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

        # calculate the largest semi-major axis and calculates scale if applicable
        semimajor_axes = []
        for entity in self.solar_system.entities:
            self.histories.append([])
            semimajor_axes.append(math.hypot(entity.x, entity.y))
        self.set_scale(max(semimajor_axes) + 0.2)

        font_dir = '{}/fonts/Inconsolata.ttf'.format(os.path.dirname(__file__))
        font = pygame.font.Font(font_dir, 14)
        clock = pygame.time.Clock()
        self.running = True
        run = 0

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
            self.window.fill((0, 0, 0))

            if self.show_history:
                for i, ent_history in enumerate(self.histories):
                    for j,  hist in enumerate(ent_history[1:]):
                        pygame.draw.line(self.window, self.solar_system.entities[i].color, hist, ent_history[j])

            entity_labels = []
            for i, entity in enumerate(self.solar_system.entities):
                # calculate pygame x, y coords
                # this zooming stuff/scale is super sketchy yikes
                relative_scale = self.scale / self.default_scale
                x = int(relative_scale * ((self.scale * entity.x) + self.dx) + self.offsetx)
                # reflected across y-axis to compensate for pygame's reversed axes
                y = int(relative_scale * ((self.scale * -entity.y) + self.dy) + self.offsety)
                r = 6
                if entity.name == 'Sun':
                    r *= 5

                pygame.draw.circle(self.window, entity.color, (x, y), r, 0)

                label = font.render(entity.name, False, (180, 180, 180))
                entity_labels.append((label, (x + 3 + r, y + 3 + r)))

                if self.show_history and not self.paused:
                    self.histories[i].append((x, y))
                    if len(self.histories[i]) > i * 150:
                        self.histories[i] = self.histories[i][1:]

            if self.show_sim_space:
                relative_scale = self.scale / self.default_scale
                x1 = int(relative_scale * ((self.scale * self.sim_space[0]) + self.dx) + self.offsetx)
                y1 = int(relative_scale * ((self.scale * -self.sim_space[1]) + self.dy) + self.offsety)
                x2 = int(relative_scale * ((self.scale * self.sim_space[2]) + self.dx) + self.offsetx)
                y2 = int(relative_scale * ((self.scale * -self.sim_space[3]) + self.dy) + self.offsety)
                c = (255, 0, 0)
                pygame.draw.rect(self.window, c, (x1, y1, x2-x1, y2-y1), 1, 5)

                text = 'Position: {}'.format(self.custom_entity['position'])
                self.window.blit(font.render(text, False, c), (x1, y2 + 0 * 15 + 3))
                text = 'Mass:     {}'.format(self.custom_entity['mass'])
                self.window.blit(font.render(text, False, c), (x1, y2 + 1 * 15 + 3))
                text = 'Speed:    {}'.format(self.custom_entity['speed'])
                self.window.blit(font.render(text, False, c), (x1, y2 + 2 * 15 + 3))
                text = 'Angle:    {}'.format(self.custom_entity['angle'])
                self.window.blit(font.render(text, False, c), (x1, y2 + 3 * 15 + 3))
                text = 'Score:    {}'.format(self.custom_entity['score'])
                self.window.blit(font.render(text, False, c), (x1, y2 + 4 * 15 + 3))

            if self.show_labels:
                for label in entity_labels:
                    text, position = label
                    self.window.blit(text, position)

            # Number of simulation steps
            c = (255, 0 if run > self.max_runs else 255, 0 if run > self.max_runs else 255)
            self.window.blit(font.render(str(run), False, c), (10, 10))

            # Disclaimer
            self.window.blit(font.render('not to scale', False, (180, 180, 180)), (self.width - 90, self.height - 20))

            pygame.display.flip()

            run += 1 if not self.paused else 0

            if run == 1001:
                self.paused = True 

            # delta_t hat zwar in der Simulation keine Auswirkung (mehr), ist aber gut für die Visualisierung
            clock.tick(60)
