from orbitalsim import simulation

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


def main(runs):

    sim_space = (
        # x1, y1, x2, y2 of simulation space
        [-0.4, 1.1, 0.4, 0.3],
        # masses that where trained
        [7e23, 5e25, 3e27]
    )

    s = simulation.Simulation(dimensions=(1000, 1000), max_runs=runs, sim_space=sim_space)

    for ent in SIM_ENTITIES:
        s.add_custom_entity(
            position=ent['position'],
            mass=ent['mass'],
            speed=ent['speed'],
            angle=ent['angle'],
            name=ent['name'],
            color=ent['color']
        )

    s.add_custom_entity(
        name='Custom',
        color=(255, 0, 0),
        position=(-0.395, 0.305),
        mass=7e25,
        speed=0.015,
        angle=None
    )

    s.start()


if __name__ == '__main__':
    main(1000)
