from math import pi as math_pi

from orbitalsim.entities import Entity



class OrbitalSystem():
    def __init__(self):
        self.entities = []

        self.bg = (0, 0, 0)

    def add_entity(
        self,
        position=(0, 0),
        mass=6e24,
        speed=0,
        angle=0,
        name='',
        color=(255, 255, 255)
    ):
        entity = Entity(position, mass, speed, angle, name, color)

        self.entities.append(entity)

    def update(self):
        for i, entity in enumerate(self.entities):
            entity.move()

            for entity2 in self.entities[i + 1:]:
                force, theta = entity.attract(entity2)

                entity.accelerate(force / entity.mass, theta - (math_pi / 2))
                
                entity2.accelerate(force / entity2.mass, theta + (math_pi / 2))
