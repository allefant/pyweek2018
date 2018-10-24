import vector
import math

class Camera:
    def __init__(self):
        self.p = vector.o.copy()
        self.unrotate()

    def unrotate(self):
        self.x = vector.x.copy() # right (-left)
        self.y = vector.y.copy() # back (-front)
        self.z = vector.z.copy() # up (-down)

    def rotate(self, axis, angle):
        self.x = self.x.rotate(axis, angle)
        self.y = self.y.rotate(axis, angle)
        self.z = self.z.rotate(axis, angle)

    def center_on(self, x, y):
        self.p = vector.Vector(x, y, 0)

    def shift(self, x, y):
        xv = vector.Vector(self.x.x, self.x.y, 0).normalize()
        yv = vector.Vector(self.y.x, self.y.y, 0).normalize()
        yv = yv * (1 + math.sin(abs(self.y.z)))
        self.p += xv * x
        self.p += yv * y
