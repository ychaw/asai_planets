import math
import numpy as np

from orbitalsim.environment import OrbitalSystem

# G * M of sun
std_grav_param = 1.32712440018e20

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
        self.sgp = 0

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

        # a = orbit's semi-major axis
        # G = gravitational constant G.to('AU3 / (kg d2)').value
        # M = mass of sun
        # r = radius of orbit

        # T = 2 * π * √( a**3 / (G * M) )   orbital period

        # v_1 = 2 * π * r / T
        # v_2 = √( G*M / r )

        # wenn v_1 > v_2 => zu schnell
        # wenn v_1 < v_2 => zu langsam

        # Abstand von v_1 zu v_2 könnte ein Maß der Stabilität sein

        dist = []

        for ent in self.solar_system.entities:
            if ent.name != sim_entities[0]['name']:
                a = math.hypot(ent.x, ent.y)
                r = math.hypot(ent.x + self.solar_system.entities[0].x, ent.y - self.solar_system.entities[0].y)
                period = 2 * math.pi * math.sqrt(a**3 / std_grav_param)
                v_1 = 2 * math.pi * r / period
                v_2 = math.sqrt(std_grav_param / r)
                dist.append(abs(v_1 - v_2))

        return dist

    def start(self, max_runs):

        self.running = True
        run = 0

        fitness = []

        while self.running:

            self.solar_system.update()

            # entweder alle x durchläufe oder einmal am ende
            if run > 0 and run % 100 == 0:
                fitness.append(self.check_if_still_stable())

            if run >= max_runs - 1:
                self.running = False
            run += 1

        data = np.array(fitness).transpose()
        print(np.nanmean((data[:, 1:]/data[:, :-1]), axis=1) - 1)


def main(runs, custom):
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
    if custom:
        s.add_custom_entity(
            name='Custom',
            position=(0.6, 0.6),
            mass=3e27,
            speed=0.008,
            angle=4
        )

    s.start(runs)


if __name__ == '__main__':
    main(1000, False)
    main(1000, True)
