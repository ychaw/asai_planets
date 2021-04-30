import p5

#
# Constants and globals
#

planets = []
G = 10  # Gravitational constant, higher values mean more gravity
# G = 6.6743015e-11  # The actual gravitational constant
framerate = 60
dt = 1/60  # This is basically dampening at this point

#
# Processing
#


def setup():
    global planets
    p5.size(1200, 800)
    # Drop in some planets
    planets.append(Body(p5.Vector(600, 330), 120, 'A'))
    planets.append(Body(p5.Vector(250, 100), 60, 'B'))
    planets.append(Body(p5.Vector(150, 200), 30, 'C'))
    planets.append(Body(p5.Vector(850, 500), 50, 'D'))

    # Give some initial velocity to a planet
    # This way we have to wait less until something happens
    planets[1].vel = p5.Vector(0.4, 0.1)


def draw():
    # Make space dark and cold... Mainly dark though.
    p5.background(0)

    # this can be optimized of course...
    for index, planet in enumerate(planets):
        force = p5.Vector(0, 0)
        for otherPlanet in planets:
            if planet is otherPlanet:
                continue
            force = force + getGravitationalForce(planet, otherPlanet)
        planet.applyForce(force)
        planet.show(True)

        # display info on planets
        infoText = planet.getInfo()
        p5.fill(255)
        p5.stroke_weight(0)
        p5.text(infoText, 10, 10 + 20 * index)


# Class representing a celestial body
class Body:
    # Pos as vector and mass as a number please :)
    # Name is mainly useful for debugging
    def __init__(self, pos, m, name=''):
        self.name = name
        self.pos = pos
        self.vel = p5.Vector(0, 0)
        self.acc = p5.Vector(0, 0)
        self.m = m
        self.col = p5.Color(r=m, g=m, b=20, color_mode='rgb')

    # Change how the body is displayed here
    def show(self, showAcc=False):
        # The actual body
        p5.stroke_weight(0.5 * self.m)
        p5.stroke(self.col)
        p5.point(self.pos.x, self.pos.y)

        # Show the (scaled up) acceleration vector for debugging
        if showAcc:
            p5.stroke_weight(2)
            accVis = self.pos + (self.m * 1000 * self.acc)
            p5.stroke(255, 120, 0)
            p5.line([self.pos.x, self.pos.y], accVis)

    # Add the force vector to the bodies acceleration
    def applyForce(self, f):
        global width, height
        # Think F=ma with dampening via dt
        self.acc = dt * (self.acc + f / self.m)
        # Actually integrating for physics is for chumps!
        self.vel = (self.vel + self.acc)
        self.pos = (self.pos + self.vel)
        # Make the body wrap around if it leaves the window
        self.pos = p5.Vector(self.pos.x % width, self.pos.y % height)

    # Get a formatted string with all the info on this body
    def getInfo(self):
        infoStrings = [
            'Body {}'.format(self.name),
            'Pos: {:.2f}, {:.2f}'.format(self.pos.x, self.pos.y),
            'Vel: {:.8f}, {:.8f}'.format(self.vel.x, self.vel.y),
            'Acc: {:.8f}, {:.8f}'.format(self.acc.x, self.acc.y),
            'Mass: {:.2f}'.format(self.m)
        ]
        info = ' '.join(infoStrings)
        return info

#
# Physics
#


# Calculate the gravitational force acting on two bodies a and b
def getGravitationalForce(a, b):
    den = (G * a.m * b.m)
    distance = a.pos.distance(b.pos)
    force = den / p5.sq(distance)
    forceVector = (b.pos - a.pos)
    forceVector.magnitude = force
    return forceVector


if __name__ == '__main__':
    p5.run(frame_rate=framerate)
