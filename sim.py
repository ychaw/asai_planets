import math
import time

from numpy import array as np_array
from numpy import sum as np_sum

from orbitalsim.environment import OrbitalSystem

SIM_ENTITIES = [
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
        'mass': 5.972e24 + 7.342e22,
        'speed': 0.017200221950579502,
        'angle': -2.9377629737585336,
        'diameter': 8.5175009e-5,
        'e': 0.01667651824711395,
        'a': 1.000011043814421
    },
]

# used to calculate systems stability
REFERENCE_SIM = [
    # Sun
    [
        (0.0, 0.0),
        (8.678877784227085e-06, 4.022976857755344e-06),
        (1.167604642848788e-05, 2.0759222586031514e-05),
        (9.60685304239119e-06, 2.725940786956828e-05),
        (1.3037752753359024e-05, 3.5053740841573836e-05),
        (1.7862309387024178e-05, 4.193067980783016e-05),
        (2.208070011814657e-05, 5.723719543846143e-05),
        (1.6985932108993513e-05, 6.368767951697934e-05),
        (2.5407703246612537e-05, 6.84222988336066e-05),
        (2.831559123304524e-05, 8.202904436274415e-05)
    ],
    # Mercury
    [
        (0.36022084228458984, -0.012291532128450675),
        (0.15078944847512493, 0.3270336816994544),
        (-0.23561370303251772, 0.3008426741915535),
        (-0.4013053001409867, -0.025535994289669336),
        (-0.223928062091154, -0.3343572448804956),
        (0.140958398457591, -0.3559117176629888),
        (0.35870297651752164, -0.03632714217835471),
        (0.17230179048902888, 0.3161921670927416),
        (-0.21510654299668763, 0.31567783161163726),
        (-0.40202266851220203, 0.0008437050574097368)
    ],
    # Venus
    [
        (0.5265819096805362, -0.5012653868869172),
        (-0.3589552219149682, 0.6153566894071542),
        (0.11744573092384163, -0.7225091762896522),
        (0.11049790754331762, 0.7006892826582741),
        (-0.3399215849122726, -0.6488357052237812),
        (0.5306835223087956, 0.4738219617939073),
        (-0.6585479784305834, -0.31092779635307183),
        (0.7167601289657808, 0.03705124449955619),
        (-0.7041334762888656, 0.15510738645255373),
        (0.5936987497437147, -0.41670069082546846)
    ],
    # Earth
    [
        (0.9756409026810421, 0.2192289865895772),
        (-0.37735597503504015, 0.9170871667173863),
        (-0.8536781472919552, -0.5264429553378432),
        (0.631841910757421, -0.7851508326603461),
        (0.6786860241773214, 0.7278934861497726),
        (-0.834036315242966, 0.5408106021434258),
        (-0.4179313215771789, -0.9161631425443509),
        (0.9582018691975686, -0.30086592611279894),
        (0.14446414135737662, 0.9815458760771556),
        (-0.9981640539664045, -0.02568826393706401)
    ]
]


class Simulation():
    def __init__(self, max_runs, collision_dist):

        self.max_runs = max_runs
        self.collision_dist = collision_dist

        # initialise the Orbital System object
        self.solar_system = OrbitalSystem()

        self.running = False
        self.planet_positions = []
        self.planet_collision = False

    def add_custom_entity(
        self,
        position,
        mass,
        speed=0,
        angle=0
    ):
        '''
        Parameters:
            position: tuple (x, y) describing the distance in AU from the centre of the system (0, 0)
            mass: measured in kg
            speed: magnitude of initial velocity measured in AU/day
            angle: angle of initial velocity given in rad
            diameter: measured in AU
        '''

        self.solar_system.add_entity(
            position=position,
            speed=speed,
            angle=angle,
            mass=mass
        )

    def get_planet_positions(self):
        # excluding custom planet
        return [(entity.x, entity.y) for entity in self.solar_system.entities[:-1]]

    def check_for_collisions(self):
        # including custom planet
        positions = self.planet_positions[-1] + [(self.solar_system.entities[-1].x, self.solar_system.entities[-1].y)]
        for i, a in enumerate(positions):
            for b in positions[i+1:]:
                dist = math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
                if dist <= self.collision_dist:
                    self.planet_collision = True
                    self.running = False
                    return

    def start(self):
        self.running = True
        run = 0

        while self.running:

            self.solar_system.update()

            # Alle x Durchläufe werden die Positionen der Planeten gespeichert
            if run % (self.max_runs / 10) == 0:
                self.planet_positions.append(self.get_planet_positions())

            # Check ob Planeten sich zu nahe gekommen sind
            self.check_for_collisions()

            # Zählen der runs -> Abbruchbedingung
            if run >= self.max_runs - 1:
                self.running = False
            run += 1

    def calc_stability(self) -> float:
        # Liste wird umstrukturiert, sodass in jedem Eintrag der Zeitverlauf eines Planeten abgebildet wird
        planets = [[] for _ in self.planet_positions[0]]

        for timestep in self.planet_positions:
            for i, planet_pos in enumerate(timestep):
                planets[i].append(planet_pos)

        diff = np_array(REFERENCE_SIM) - np_array(planets)
        return np_sum(diff)


def simulate_orbital_system(max_runs:int=1000, collision_dist:float=0.001, stability_cutoff:float=3, custom_entity:dict=None):
    '''
    Simulation of the inner four planets of our solar system (Sun, Mercury, Venus, Earth) with an optional added custom planet.

            Parameters:
                    max_runs           (int): The number of simulation steps (time)
                    collision_dist   (float): The distance from which planets collide (in AU)
                    stability_cutoff (float): Used to adjust the score, higher values mean less strict scoring system
                    custom_entity     (dict): Dictionary with position (x, y), mass, speed and angle all as floats

            Returns:
                    score (float): Score from 0 to 1 that represents the stability of the system (0: bad, 1:good)
    '''
    s = Simulation(max_runs, collision_dist)

    for ent in SIM_ENTITIES:
        s.add_custom_entity(
            position=ent['position'],
            mass=ent['mass'],
            speed=ent['speed'],
            angle=ent['angle']
        )

    if custom_entity != None:
        s.add_custom_entity(
            position=custom_entity['position'],
            mass=custom_entity['mass'],
            speed=custom_entity['speed'],
            angle=custom_entity['angle']
        )

    s.start()

    score = stability_cutoff
    if not s.planet_collision:
        score = s.calc_stability()

    # score comes in the range of 0 (best possible outcome) to inf (worst outcome)
    # here we cap the score to a maximum value of 5
    score = min(score, stability_cutoff)

    # lerping score so that the minimum value (worst) is 0 and the maximum value (best) is 1
    score = score / stability_cutoff * -1 + 1

    return score


if __name__ == '__main__':

    max_runs = 1000
    collision_dist = 0.001
    stability_cutoff = 3
    custom_entity = {
        'position': (1., 1.),
        'mass': 3.e26,
        'speed': 0.014,
        'angle': 4.
    }
    start = time.time()

    score = simulate_orbital_system(max_runs, collision_dist, stability_cutoff, custom_entity)

    print(f'\nScore:        {score:.10f}\nTime Elapsed: {time.time() - start:.3f}\n')
