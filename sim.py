import math
import time

from orbitalsim.environment import OrbitalSystem

sim_entities = [
    {
        'name': 'Sun',
        'color': (245, 236, 111),
        'position': (0, 0),
        'mass': 1.9884e30,
        'speed': 0,
        'angle': 0,
        'diameter': 9.309624485e-3,
        'e': 0,
        'a': 0
    },
    {
        'name': 'Mercury',
        'color': (155, 154, 142),
        'position': (0.3590961172798053, -0.04164522874752517),
        'mass': 3.285e23,
        'speed': 0.029287836754110234,
        'angle': -3.2570492550785675,
        'diameter': 3.26167744e-5,
        'e': 0.2056214963443691,
        'a': 0.3870993130750688
    },
    {
        'name': 'Venus',
        'color': (237, 200, 132),
        'position': (0.5127350527183985, -0.5158182472028876),
        'mass': 4.867e24,
        'speed': 0.02008004590994939,
        'angle': -3.9299884110350813,
        'diameter': 8.0910243e-5,
        'e': 0.006775865311086034,
        'a': 0.7233300921935613
    },
    {
        'name': 'Earth',
        'color': (95, 135, 195),
        'position': (0.97941231066402, 0.2024447197289333),
        'mass': 5.972e24,
        'speed': 0.017200221950579502,
        'angle': -2.9377629737585336,
        'diameter': 8.5175009e-5,
        'e': 0.01667651824711395,
        'a': 1.000011043814421
    },
]


class Simulation():
    def __init__(self):

        # initialise the Orbital System object
        self.solar_system = OrbitalSystem()

        self.running = False

    def add_custom_entity(
        self,
        position,
        mass,
        speed=0,
        angle=0,
        diameter=1e-5,
        e=0,
        a=None,
        name=''
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
            name=name
        )

    """
    Main simulation function
    """

    def check_if_still_stable(self):
        for ent in self.solar_system.entities:
            print(ent.name, ent.x, ent.y)
        print()

    def start(self):
        start = time.time()
        simulation_period = 0.01

        self.running = True

        while self.running:

            if time.time() > start + simulation_period:
                self.running = False
                break

            self.solar_system.update()
            self.check_if_still_stable()


def main():
    s = Simulation()

    for ent in sim_entities:
        s.add_custom_entity(
            position=ent['position'],
            mass=ent['mass'],
            speed=ent['speed'],
            angle=ent['angle'],
            diameter=ent['diameter'],
            e=ent['e'],
            a=ent['a'],
            name=ent['name']
        )

    s.start()


if __name__ == '__main__':
    main()
