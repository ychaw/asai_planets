import math
from numba import jit, float64, byte
from numba.types import UniTuple, unicode_type
from numba.experimental import jitclass

@jit(nopython=True, nogil=True, signature_or_function=UniTuple(float64, 2)(float64, float64, float64, float64))
def add_vectors(mag1, angle1, mag2, angle2):
    # vectors are quantities with a magnitude and direction
    # add them by connecting them end-to-end to form one resulting vector
    # add the x and y components together to get a right-angled triangle with hypotenuse of the resulting vector's magnitude
    x = mag1 * math.sin(angle1) + mag2 * math.sin(angle2)
    y = mag1 * math.cos(angle1) + mag2 * math.cos(angle2)

    # use Pythagoras to find the magnitude of the resulting vector
    mag = math.hypot(x, y)
    # use inverse trig to find the angle of the right-angled triangle, take away from 90deg to get the resulting vecotr's angle
    # atan2 takes care of x = 0
    angle = (math.pi / 2) - math.atan2(y, x)

    return mag, angle


"""
Main entity class
"""


spec = [
    ('x', float64),
    ('y', float64),
    ('mass', float64),
    ('speed', float64),
    ('angle', float64),
    ('name', unicode_type),
    ('color', UniTuple(byte, 3)),
]

@jitclass(spec)
class Entity():
    def __init__(self, position, mass, speed, angle, name, color):
        # position: tuple (x, y) describing the distance in AU from the centre of the system (0, 0)
        # mass: measured in kg
        # speed: magnitude of initial velocity measured in AU/day
        # angle: angle of initial velocity given in rad
        self.x, self.y = position
        self.mass = mass
        self.speed = speed
        self.angle = angle
        self.color = color
        self.name = name


    """
    Physics calculations for movement
    """

    def move(self):
        # adjust speed for days past per frame
        # calculates next x, y position
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed  # subtract because of pygame's coord system

    
    def accelerate(self, mag, angle):
        # combine apply acceleration to velocity vector
        new = add_vectors(self.speed, self.angle, mag, angle)
        self.speed = new[0]
        self.angle = new[1]

    
    def attract(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        theta = math.atan2(dy, dx)
        distance = math.hypot(dx, dy)

        # calculate attractive force due to gravity using Newton's law of universal gravitation:
        # F = G * m1 * m2 / r^2
        # for consistency, G = [AU^3 * kg^-1 * d^-2]
        # 1.4881851702345193e-34 = G.to('AU3 / (kg d2)').value
        force = float64(1.4881851702345193e-34) * self.mass * other.mass / (distance ** 2)

        # accelerate both bodies towards each other by acceleration vector a = F/m, rearranged from Newton's second law
        return force, theta
