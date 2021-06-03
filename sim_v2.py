import math
import time

from numba import float64, jit
from numba.types import UniTuple
from numpy import array as np_array
from numpy import sum as np_sum
from numpy import abs as np_abs

SIM_ENTITIES = [
    {
        'name': 'Sun',
        'color': (245, 236, 111),
        'position': (0, 0),
        'mass': 1.9884e30,
        'speed': 0,
        'angle': 0
    },
    {
        'name': 'Mercury',
        'color': (155, 154, 142),
        'position': (0.3590961172798053, -0.04164522874752517),
        'mass': 3.285e23,
        'speed': 0.029287836754110234,
        'angle': -3.2570492550785675
    },
    {
        'name': 'Venus',
        'color': (237, 200, 132),
        'position': (0.5127350527183985, -0.5158182472028876),
        'mass': 4.867e24,
        'speed': 0.02008004590994939,
        'angle': -3.9299884110350813
    },
    {
        'name': 'Earth',
        'color': (95, 135, 195),
        'position': (0.97941231066402, 0.2024447197289333),
        'mass': 5.972e24 + 7.342e22,
        'speed': 0.017200221950579502,
        'angle': -2.9377629737585336
    },
]

# used to calculate systems stability
REFERENCE_SIM = [
    [(0.0,                    0.0),                    (0.36022084228458984, -0.012291532128450675),  (0.5265819096805362,  -0.5012653868869172),  (0.9756409026810421,   0.2192289865895772)],
    [(8.678877784227085e-06,  4.022976857755344e-06),  (0.15078944847512493,  0.3270336816994544),    (-0.3589552219149682,  0.6153566894071542),  (-0.37735597503504015, 0.9170871667173863)],
    [(1.167604642848788e-05,  2.0759222586031514e-05), (-0.23561370303251772, 0.3008426741915535),    (0.11744573092384163, -0.7225091762896522),  (-0.8536781472919552, -0.5264429553378432)],
    [(9.60685304239119e-06,   2.725940786956828e-05),  (-0.4013053001409867, -0.025535994289669336),  (0.11049790754331762,  0.7006892826582741),  (0.631841910757421,   -0.7851508326603461)],
    [(1.3037752753359024e-05, 3.5053740841573836e-05), (-0.223928062091154,  -0.3343572448804956),    (-0.3399215849122726, -0.6488357052237812),  (0.6786860241773214,   0.7278934861497726)],
    [(1.7862309387024178e-05, 4.193067980783016e-05),  (0.140958398457591,   -0.3559117176629888),    (0.5306835223087956,   0.4738219617939073),  (-0.834036315242966,   0.5408106021434258)],
    [(2.208070011814657e-05,  5.723719543846143e-05),  (0.35870297651752164, -0.03632714217835471),   (-0.6585479784305834, -0.31092779635307183), (-0.4179313215771789, -0.9161631425443509)],
    [(1.6985932108993513e-05, 6.368767951697934e-05),  (0.17230179048902888,  0.3161921670927416),    (0.7167601289657808,   0.03705124449955619), (0.9582018691975686,  -0.30086592611279894)],
    [(2.5407703246612537e-05, 6.84222988336066e-05),   (-0.21510654299668763, 0.31567783161163726),   (-0.7041334762888656,  0.15510738645255373), (0.14446414135737662,  0.9815458760771556)],
    [(2.831559123304524e-05,  8.202904436274415e-05),  (-0.40202266851220203, 0.0008437050574097368), (0.5936987497437147,  -0.41670069082546846), (-0.9981640539664045, -0.02568826393706401)]
]


@jit(nopython=True, signature_or_function=UniTuple(float64, 2)(UniTuple(float64, 2), float64, float64))
def move(positions: tuple[float, float], angle: float, speed: float) -> tuple[float, float]:
    return positions[0] + math.sin(angle) * speed, positions[1] - math.cos(angle) * speed


@jit(nopython=True, signature_or_function=UniTuple(float64, 2)(UniTuple(float64, 2), UniTuple(float64, 2), float64, float64))
def attract(pos1: tuple[float, float], pos2: tuple[float, float], mass1: float, mass2: float) -> tuple[float, float]:
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    theta = math.atan2(dy, dx)
    distance = math.hypot(dx, dy)
    if distance == 0:
        distance = 0.000000000001
    force = 1.4881851702345193e-34 * mass1 * mass2 / (distance ** 2)
    return force, theta


@jit(nopython=True, signature_or_function=UniTuple(float64, 2)(float64, float64, float64, float64))
def add_vectors(speed1: float, angle1: float, speed2: float, angle2: float) -> tuple[float, float]:
    x = speed1 * math.sin(angle1) + speed2 * math.sin(angle2)
    y = speed1 * math.cos(angle1) + speed2 * math.cos(angle2)
    speed = math.hypot(x, y)
    angle = (math.pi / 2) - math.atan2(y, x)
    return speed, angle


def planets_did_collide(positions: list[tuple[float, float]], collision_dist: float) -> bool:
    for i, a in enumerate(positions):
        for b in positions[i+1:]:
            dist = math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
            if dist <= collision_dist:
                return True
    return False


def calc_stability(planet_history: list[list[tuple[float, float]]]) -> float:
    diff = np_abs(np_array(REFERENCE_SIM) - np_array(planet_history))
    return np_sum(diff)


def simulate_orbital_system(max_runs: int = 1000, collision_dist: float = 0.001, stability_cutoff: float = 3, custom_entity: dict = None, check_for_collisions: bool = True) -> float:
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

    positions = []
    masses = []
    speeds = []
    angles = []

    planet_history = []

    num_of_entities = 0

    running = True
    run = 0

    planet_collision = False

    for ent in SIM_ENTITIES:
        positions.append(ent['position'])
        masses.append(ent['mass'])
        speeds.append(ent['speed'])
        angles.append(ent['angle'])
        num_of_entities += 1

    if custom_entity is not None:
        positions.append(custom_entity['position'])
        masses.append(custom_entity['mass'])
        speeds.append(custom_entity['speed'])
        angles.append(custom_entity['angle'])

        # If the angle is None, calculate the angle perpendicular to the sun
        if angles[-1] is None:
            angles[-1] = math.atan2(positions[-1][1], positions[-1][0]) + math.pi

        num_of_entities += 1

    while running:

        # update solar system
        for i in range(num_of_entities):

            positions[i] = move(positions[i], angles[i], speeds[i])

            for j in range(i+1, num_of_entities):
                force, theta = attract(positions[i], positions[j], masses[i], masses[j])

                speed_angle1 = add_vectors(speeds[i], angles[i], force / masses[i], theta - (math.pi / 2))
                speeds[i] = speed_angle1[0]
                angles[i] = speed_angle1[1]

                speed_angle2 = add_vectors(speeds[j], angles[j], force / masses[j], theta + (math.pi / 2))
                speeds[j] = speed_angle2[0]
                angles[j] = speed_angle2[1]

        # Alle x Durchläufe werden die Positionen der Planeten gespeichert
        if run % (max_runs / 10) == 0:
            if custom_entity is None:
                planet_history.append(positions[:])
            else:
                planet_history.append(positions[:-1])

        # Check ob Planeten sich zu nahe gekommen sind
        if check_for_collisions:
            if planets_did_collide(positions, collision_dist):
                planet_collision = True
                running = False

        # Zählen der runs -> Abbruchbedingung
        if run >= max_runs - 1:
            running = False
        run += 1

    score = stability_cutoff
    if not planet_collision:
        score = calc_stability(planet_history)

    # score comes in the range of 0 (best possible outcome) to inf (worst outcome)
    # here we cap the score to a maximum value of stability_cutoff and minimum 0
    score = max(0, min(score, stability_cutoff))

    # lerping score so that the minimum value (worst) is 0 and the maximum value (best) is 1
    score = (score / stability_cutoff) * -1 + 1

    return score


if __name__ == '__main__':

    max_runs = 1000
    collision_dist = 0.001
    stability_cutoff = 15
    custom_entity = {
        'position': (-0.4, -0.4),
        'mass': 7e23,
        'speed': 0.015,
        'angle': None
    }
    start = time.time()

    score = simulate_orbital_system(max_runs, collision_dist, stability_cutoff, custom_entity)

    print(f'\nScore:        {score:.10f}\nTime Elapsed: {time.time() - start:.3f}\n')
