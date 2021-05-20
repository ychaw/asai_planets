from orbitalsim import simulation

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


def main(runs, stable):
    s = simulation.Simulation(dimensions=(1000, 1000), max_runs=runs)

    for ent in SIM_ENTITIES:
        s.add_custom_entity(
            position=ent['position'],
            mass=ent['mass'],
            speed=ent['speed'],
            angle=ent['angle'],
            diameter=ent['diameter'],
            e=ent['e'],
            a=ent['a'],
            name=ent['name'],
            color=ent['color']
        )

    s.add_custom_entity(
        name='Custom',
        color=(255, 0, 0),
        position=(1, 0.5),
        mass=3e24,
        speed=0.014,
        angle=4
    )

    s.start()


if __name__ == '__main__':

    main(1000, False)
