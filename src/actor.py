import camera
import vector
import random
import game
import math

FLOWING = 0
FALLING = 1

class Actors:
    def __init__(self):
        self.actors = []
        self.grid = []
        self.xos = 0
        self.yos = 0
        for i in range(32 * 32):
            self.grid.append([])

    def new(self, profession, x, y):
        a = Actor(profession, x, y)
        self.actors.append(a)
        self.grid_place(a)
        return a

    def __iter__(self):
        return iter(self.actors)

    def remove(self, a):
        self.grid_unplace(a)
        self.actors.remove(a)

    def get_cell_at(self, x, y):
        x = math.floor(x / 8)
        y = math.floor(y / 8)
        return (x & 31) * 32 + (y & 31)

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
        cell1 = self.get_cell_at(a.cam.p.x - 1, a.cam.p.y - 1)
        cells = [cell1]
        cell2 = self.get_cell_at(a.cam.p.x + 1, a.cam.p.y - 1)
        if cell2 != cell1: cells += [cell2]
        cell3 = self.get_cell_at(a.cam.p.x - 1, a.cam.p.y + 1)
        if cell3 != cell1: cells += [cell3]
        cell4 = self.get_cell_at(a.cam.p.x + 1, a.cam.p.y + 1)
        if cell4 != cell2 and cell4 != cell3: cells += [cell4]

        for x in cells:
            for c in self.grid[x]:
                if a.collides(c):
                    yield c

class Actor:
    def __init__(self, profession, x, y):
        self.profession = profession
        self.cam = camera.Camera()
        self.cam.rotate(vector.z, math.pi / 2)
        z = game.get().landscape.get_height_interpolated(x, y)
        self.cam.p += (x, y, z)
        self.frame_t = random.randint(0, 7)
        self.v = vector.o
        self.t = 0
        self.state = FLOWING

    def collides(self, c):
        if c is self: return False
        d = self.cam.p - c.cam.p
        if d.length() < 1 + 1:
            return True
        return False
        
    def turn(self, angle):
        self.cam.rotate(vector.z, angle)

    def tick(self, actors):
        g = game.get()

        if self.state == FALLING:
            self.v *= 0.98
            self.v += (0.33, 0, -1)
            self.cam.p = self.cam.p + self.v * 0.01
            return

        self.v *= 0.98
        self.v = self.v + (0.2, 0, -0.3)

        cell1 = actors.get_cell(self)
        self.cam.p = self.cam.p + self.v * 0.01

        for c in actors.get_colliders(self):
            d = self.cam.p - c.cam.p
            n = d.normalize()
            self.cam.p += n * (2 - d.length())
            response = 2 * (self.v * n) * n
            self.v -= response / 2
            c.v += response / 2

        friction = 0.93
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

        if self.cam.p.x < 0 or self.cam.p.y < 0 or self.cam.p.y > 128:
            self.state = FALLING

        cell2 = actors.get_cell(self)
        if cell2 != cell1:
            actors.move(cell1, cell2, self)
    
