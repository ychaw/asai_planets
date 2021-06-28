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


def start_visualization(runs, sim_space, custom_entity):

    s = simulation.Simulation(dimensions=(1000, 1000), max_runs=runs, sim_space=sim_space, custom_entity=custom_entity)

    for ent in SIM_ENTITIES:
        s.add_custom_entity(
            position=ent['position'],
            mass=ent['mass'],
            speed=ent['speed'],
            angle=ent['angle'],
            name=ent['name'],
            color=ent['color']
        )

    if custom_entity is not None:
        s.add_custom_entity(
            position=custom_entity['position'],
            mass=custom_entity['mass'],
            speed=custom_entity['speed'],
            angle=custom_entity['angle'],
            name=custom_entity['name'],
            color=custom_entity['color']
        )

    s.start()


if __name__ == '__main__':
    
    # x1, y1, x2, y2 of simulation space
    sim_space = [-1.5, 1.5, 1.5, -1.5]

    custom_entity = {
        'name': 'Custom',
        'color': (255, 0, 0),
        'position': (0.12140175219023774, -0.8197747183979975),
        'mass': 5e27,
        'speed': 0.015,
        'angle': None,
        'score': None
    }

    start_visualization(1000, sim_space, custom_entity)
