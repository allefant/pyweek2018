import camera
import vector
import random
import game
import math
from math import pi
import audio

FLOWING = 0
FALLING = 1
DIVING = 2
EATEN = 3
GONE = 4
WON = 5

class Actors:
    def __init__(self, landscape):
        self.landscape = landscape
        self.actors = []
        self.grid = []
        self.xos = 0
        self.yos = 0
        for i in range(16 * 8 * 8):
            self.grid.append([])

    def new(self, profession, x, y, **params):
        a = Actor(profession, x, y, self.landscape)
        a.static = False
        self.grid_place(a)
        for key, val in params.items():
            if key == "flying": a.flying = val
            if key == "scale": a.scale = val
            if key == "z": a.cam.p.z = val
            if key == "static": a.static = True
            if key == "radius": a.radius = val
        if not a.static:
            self.actors.append(a)
        return a

    def __iter__(self):
        return iter(self.actors)

    def remove(self, a):
        self.grid_unplace(a)
        self.actors.remove(a)

    def get_cell_at(self, x, y):
        x = math.floor(x / 16)
        y = math.floor(y / 16)
        return (x & 127) + 8 * (y & 7)

    def get_cell(self, a):
        x = a.cam.p.x
        y = a.cam.p.y
        return self.get_cell_at(x, y)

    def grid_place(self, a):
        cell = self.get_cell(a)
        self.grid[cell].append(a)

    def grid_unplace(self, a):
        cell = self.get_cell(a)
        self.grid[cell].remove(a)

    def move(self, cell1, cell2, a):
        self.grid[cell1].remove(a)
        self.grid[cell2].append(a)

    def get_colliders(self, a):
        r = a.radius
        cell1 = self.get_cell_at(a.cam.p.x - r, a.cam.p.y - r)
        cells = [cell1]
        cell2 = self.get_cell_at(a.cam.p.x + r, a.cam.p.y - r)
        if cell2 != cell1: cells += [cell2]
        cell3 = self.get_cell_at(a.cam.p.x - r, a.cam.p.y + r)
        if cell3 != cell1: cells += [cell3]
        cell4 = self.get_cell_at(a.cam.p.x + r, a.cam.p.y + r)
        if cell4 != cell2 and cell4 != cell3: cells += [cell4]

        for x in cells:
            for c in self.grid[x]:
                if a.collides(c):
                    yield c

class Actor:
    def __init__(self, profession, x, y, landscape):
        self.profession = profession
        self.cam = camera.Camera()
        z = landscape.get_height_interpolated(x, y)
        self.cam.p += (x, y, z)
        self.frame_t = random.randint(0, 7)
        self.v = vector.o
        self.t = 0
        self.state = FLOWING
        self.flying = False
        self.scale = 2.5
        self.radius = 3
        self.target = None
        self.swoosh = None
        self.swoosh_xos = 0
        self.swoosh_yos = 0
        self.swoosh_t = 0
        self.xos = 0
        self.yos = 0
        self.gray = 0

        self.ground_normal = vector.z

    def collides(self, c):
        r = self.radius
        if c is self: return False
        cr = c.radius
        d = self.cam.p - c.cam.p
        if d * d < (r + cr) * (r + cr):
            return True
        return False
        
    def turn(self, angle):
        self.cam.rotate(vector.z, angle)

    def tick(self, actors):
        g = game.get()

        cell1 = actors.get_cell(self)

        if self.state == FALLING:
            self.v *= 0.98
            self.v += (0.33, 0, -1)
            self.cam.p = self.cam.p + self.v * 0.01
            if g.t > self.t + 60 * 5:
                self.state = GONE

        elif self.state == EATEN:
            self.cam.p = g.dragon.cam.p - g.dragon.cam.y * 10
            if g.t > self.t:
                self.state = FALLING
                audio.play(g.yelp)
            
        elif self.state == DIVING:
            mouthpos = self.cam.p - self.cam.y * 10
            dist = self.target.cam.p - mouthpos
            v = dist.normalize()
            self.v = self.v + v * 0.2
            
            self.cam.p = self.cam.p + self.v * 0.01
            if self.cam.get_down() < pi * 0.3:
                self.cam.rotate(self.cam.x, -0.02)
            if mouthpos.z < self.target.cam.p.z + 3:
                self.state = FLOWING
                if dist.length() < 5:
                    self.target.state = EATEN
                    self.target.t = g.t + 120
                    self.target = None
                    audio.play(g.roar)
                    self.gray = 1

        elif self.state == WON:
            self.v *= 0.98
            if self.cam.p.z < 20:
                self.v += (0, 0, 0.2)
            self.cam.p = self.cam.p + self.v * 0.01
            self.collide_with_objects(actors)
            self.cam.p.x = g.landscape.w - 1
        else:
            self.v *= 0.98 if self.cam.p.z > -15 else 1.0
            if self.flying:

                if self.cam.get_down() > 0:
                    self.cam.rotate(self.cam.x, 0.02)

                if self.cam.p.z < 20:
                    self.v = self.v + (0, 0, 0.5)
                
                if self.target:
                    v = self.target.cam.p - (self.cam.p - self.cam.y * 10)
                    v.z = 0
                    if v.length() < 5:
                        self.state = DIVING
                    else:
                        v = v.normalize()
                        self.v = self.v + (v.x * 0.22, v.y * 0.22)
                else:
                    self.v = self.v + (0.15, 0, 0)
            else:
                self.v = self.v + (0.2, 0, -0.3)

            if self.swoosh_t > g.t:
                self.v += self.swoosh

            self.cam.p = self.cam.p + self.v * 0.01

            self.collide_with_objects(actors)

            friction = 0.93 if self.cam.p.z > -15 else 1.0
            zg = g.landscape.get_height_interpolated(self.cam.p.x, self.cam.p.y)
            if self.cam.p.z < zg:
                amount = zg - self.cam.p.z
                self.cam.p.z = zg
                #      v    normal
                #      |   /
                #      |  /    v'
                # -_   | /  _-'
                #   '-_|/_-'
                #      '-_
                #         '-_
                #
                # reflection of a vector by a normal
                # v' = v - 2 * (v . n) * n
                n = g.landscape.get_normal(self.cam.p.x, self.cam.p.y)
                self.v = self.v - 2 * (self.v * n) * n
                self.v *= friction
                self.v += (0.3, 0, 0)

                self.ground_normal = n

            # if self.cam.p.x < 0:
                # self.v = self.v - 2 * (self.v * vector.x) * vector.x
                # self.cam.p.x = 0
                # self.v *= friction
            # if self.cam.p.x > 128 * 8:
                # self.v = self.v - 2 * (self.v * -vector.x) * -vector.x
                # self.cam.p.x = 128 * 8
                # self.v *= friction
            # if self.cam.p.y < 0:
                # self.v = self.v - 2 * (self.v * vector.y) * vector.y
                # self.cam.p.y = 0
                # self.v *= friction
            # if self.cam.p.y > 128:
                # self.v = self.v - 2 * (self.v * -vector.y) * -vector.y
                # self.cam.p.y = 128
                # self.v *= friction

            if not self.flying:
                if self.cam.p.x < 0 or self.cam.p.y < 0 or self.cam.p.y > 128:
                    self.state = FALLING
                    audio.play(g.yelp)
                    self.t = g.t
                    self.gray = 1

                if self.cam.p.x > g.landscape.w:
                    self.cam.p.x = g.landscape.w - 1
                    self.state = WON
                    audio.play(g.jingle)
                    self.t = g.t

        d = self.cam.get_heading() - math.atan2(self.v.x, self.v.y)
        if d < -pi: d += pi * 2
        if d > pi: d -= pi * 2
        step = math.pi / 300
        if d < -step: self.cam.rotate(vector.z, -step)
        if d > step: self.cam.rotate(vector.z, step)

        cell2 = actors.get_cell(self)
        if cell2 != cell1:
            actors.move(cell1, cell2, self)
            
    def collide_with_objects(self, actors):
        for c in actors.get_colliders(self):
            d = self.cam.p - c.cam.p
            n = d.normalize()
            r = self.radius + c.radius
            self.cam.p += n * (r - d.length())
            response = 2 * (self.v * n) * n
            self.v -= response / 2
            c.v += response / 2
