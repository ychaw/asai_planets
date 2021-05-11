import math
import datetime

from astroquery.jplhorizons import Horizons
from astropy.time import Time


def get_horizons_positioning(start_date, entity_id, observer_id):

    date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

    obj = Horizons(
        id=entity_id,
        location=f'@{observer_id}',
        epochs=Time(date).jd,
        id_type='id'
    )

    if entity_id != observer_id:
        vectors = obj.vectors()
        elements = obj.elements()

        # get the eccentricity (e) and semimajor axis (a)
        e = elements['e'].data[0]
        a = elements['a'].data[0]
        name = elements['targetname'].data[0]
        name = name[:name.rfind(' Barycenter')]
        name = name[:name.rfind('-')]

        # get the components of position and velocity from JPL SSD
        x, y = vectors['x'][0], vectors['y'][0]
        vx, vy = vectors['vx'][0], vectors['vy'][0]
        speed = math.hypot(vx, vy)

        # calculate angle of velocity by finding the tangent to the orbit
        # pygame specific: horizontally reflect the angle due to reversed y-axis
        angle = math.pi - ((2 * math.pi) - math.atan2(y, x))

        return {
            'name': name,
            'color': None,
            'position': (x, y),
            'mass': None,
            'speed': speed,
            'angle': angle,
            'diameter': None,
            'e': e,
            'a': a
        }


def get_all_horizons(date):
    return [
        get_horizons_positioning(date, '1', 'sun'),
        get_horizons_positioning(date, '2', 'sun'),
        get_horizons_positioning(date, '3', 'sun'),
    ]


def main():
    print(get_all_horizons('2021-10-05'))


if __name__ == '__main__':
    main()
