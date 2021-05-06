import orbitalsim

solar_system = [
    {
        'id': 'sun',
        'mass': 1.9884e30,
        'diameter': 9.309624485e-3
    },
    {
        'id': '1',
        'mass': 3.285e23,
        'diameter': 3.26167744e-5
    },
    {
        'id': '2',
        'mass': 4.867e24,
        'diameter': 8.0910243e-5
    },
    {
        'id': '3',
        'mass': 5.972e24,
        'diameter': 8.5175009e-5
    },
]


def main():
    s = orbitalsim.Simulation(
        dimensions=(1000, 1000)
    )

    for obj in solar_system:
        s.add_horizons_entity(
            entity_id=obj['id'],
            observer_id='sun',
            mass=obj['mass'],
            diameter=obj['diameter']
        )

    s.add_custom_entity(
        name='Custom',
        position=(0.6, 0.6),
        mass=3e24,
        speed=-0.01,
        angle=3
    )

    s.start()


if __name__ == '__main__':
    main()
