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


@jit(nopython=True, signature_or_function=UniTuple(float64, 2)(UniTuple(float64, 2), float64, float64))
def move(positions: tuple[float, float], angle: float, speed: float) -> tuple[float, float]:
    return positions[0] + math.sin(angle) * speed, positions[1] - math.cos(angle) * speed


@jit(nopython=True, signature_or_function=UniTuple(float64, 2)(UniTuple(float64, 2), UniTuple(float64, 2), float64, float64))
def attract(pos1: tuple[float, float], pos2: tuple[float, float], mass1: float, mass2: float) -> tuple[float, float]:
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    theta = math.atan2(dy, dx)
    distance = math.hypot(dx, dy)
    distance = 1e-12 if distance == 0 else distance
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


def calc_stability(reference_sim: list[list[tuple[float, float]]], planet_history: list[list[tuple[float, float]]]) -> float:
    diff = np_abs(np_array(reference_sim) - np_array(planet_history))
    return np_sum(diff)


def simulate_orbital_system(
        max_runs: int = 1000, 
        collision_dist: float = 0.001, 
        stability_cutoff: float = 3, 
        reference_sim: list[list[tuple[float, float]]] = None, 
        custom_entity: dict = None, 
        check_for_collisions: bool = True, 
        create_reference_sim: bool = False
    ) -> float:
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
    if not planet_collision and not create_reference_sim:
        score = calc_stability(reference_sim, planet_history)

    # score comes in the range of 0 (best possible outcome) to inf (worst outcome)
    # here we cap the score to a maximum value of stability_cutoff and minimum 0
    score = max(0, min(score, stability_cutoff))

    # lerping score so that the minimum value (worst) is 0 and the maximum value (best) is 1
    score = (score / stability_cutoff) * -1 + 1

    return score, planet_history


if __name__ == '__main__':

    max_runs = 1000
    collision_dist = 0.001
    stability_cutoff = 15
    custom_entity = {
        'position': (0.8698372966207759, 0.9649561952440551),
        'mass': 5e27,
        'speed': 0.015,
        'angle': None
    }
    start = time.time()

    _, reference_sim = simulate_orbital_system(max_runs, collision_dist, stability_cutoff, None, None, True, True)

    score, _ = simulate_orbital_system(max_runs, collision_dist, stability_cutoff, reference_sim, custom_entity, True, False)

    print(f'\nScore:        {score:.10f}\nTime Elapsed: {time.time() - start:.3f}\n')
