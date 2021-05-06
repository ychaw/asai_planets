import math
import datetime
import time
from astroquery.jplhorizons import Horizons
from astropy.time import Time

from orbitalsim.environment import OrbitalSystem

sim_entities = [
    {
        'name': 'sun',
        'position': (0, 0),
        'mass': 1.9884e30,
        'speed': 0,
        'angle': 0,
        'diameter': 9.309624485e-3,
        'e': 0,
        'a': 0
    },
    {
        'name': 'mercury',
        'position': (0.3590961172798053, -0.04164522874752517),
        'mass': 3.285e23,
        'speed': 0.029287836754110234,
        'angle': -3.2570492550785675,
        'diameter': 3.26167744e-5,
        'e': 0.2056214963443691,
        'a': 0.3870993130750688
    },
    {
        'name': 'venus',
        'position': (0.5127350527183985, -0.5158182472028876),
        'mass': 4.867e24,
        'speed': 0.02008004590994939,
        'angle': -3.9299884110350813,
        'diameter': 8.0910243e-5,
        'e': 0.006775865311086034,
        'a': 0.7233300921935613
    },
    {
        'name': 'earth',
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
    def __init__(self, sim_rate=3, start_date=None):

        if start_date:
            self.date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        else:
            self.date = datetime.datetime.today()

        # initialise the Orbital System object
        self.solar_system = OrbitalSystem()

        self.sim_rate = sim_rate
        self.running = False

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

    def add_horizons_entity(self, entity_id, observer_id, mass, diameter=1e-5):
        # entity_id, observer_id: the numerical ids designated by JPL SSD Horizons
        x, y, speed, angle, e, a, name = self.get_horizons_positioning(
            entity_id, observer_id)

        self.solar_system.add_entity(
            position=(x, y),
            speed=speed,
            angle=angle,
            mass=mass,
            diameter=diameter,
            e=e,
            a=a,
            name=name
        )

    def get_horizons_positioning(self, entity_id, observer_id):
        obj = Horizons(
            id=entity_id,
            location='@{}'.format(observer_id),
            epochs=Time(self.date).jd,
            id_type='id'
        )

        if not entity_id == observer_id:
            vectors = obj.vectors()
            elements = obj.elements()

            # get the eccentricity (e) and semimajor axis (a)
            e = elements['e'].data[0]
            a = elements['a'].data[0]
            name = elements['targetname'].data[0].replace('Barycenter ', '')

            # get the components of position and velocity from JPL SSD
            x, y = vectors['x'], vectors['y']
            vx, vy = vectors['vx'], vectors['vy']
            speed = math.hypot(vx, vy)

            # calculate angle of velocity by finding the tangent to the orbit
            # pygame specific: horizontally reflect the angle due to reversed y-axis
            angle = math.pi - ((2 * math.pi) - math.atan2(y, x))

            return x, y, speed, angle, e, a, name
        else:
            # special case for the central body of a system (e.g. the sun)
            # obj.elements() does not work for when entity_id and observer_id are the same
            name = obj.vectors()['targetname'].data[0].replace(
                'Barycenter ', '')
            return 0, 0, 0, 0, 0, 0, name

    def get_all_horizons(self):
        print()
        print(self.get_horizons_positioning('sun', 'sun'))
        print()
        print(self.get_horizons_positioning('1', 'sun'))
        print()
        print(self.get_horizons_positioning('2', 'sun'))
        print()
        print(self.get_horizons_positioning('3', 'sun'))
        print()

    """
    Main simulation function
    """

    def check_if_still_stable(self):
        for ent in self.solar_system.entities:
            print(ent.days_per_update())
            print(ent.name, ent.x, ent.y)
        print()

    def start(self):
        start = time.time()
        simulation_period = 0.01

        delta_t = 1

        for entity in self.solar_system.entities:
            entity.sim_rate = self.sim_rate

        self.running = True

        while self.running:

            if time.time() > start + simulation_period:
                self.running = False
                break

            self.check_if_still_stable()
            self.solar_system.update(delta_t)


def main():
    s = Simulation(sim_rate=1000, start_date='2021-10-05')

    # produces above numbers (sim_entities)
    # s.get_all_horizons()

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
