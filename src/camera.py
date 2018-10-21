import vector
import math

class Camera:
    def __init__(self):
        self.p = vector.o.copy()
        self.x = vector.x.copy() # right (-left)
        self.y = vector.y.copy() # back (-front)
        self.z = vector.z.copy() # up (-down)

    def rotate(self, axis, angle):
        self.x = self.x.rotate(axis, angle)
        self.y = self.y.rotate(axis, angle)
        self.z = self.z.rotate(axis, angle)

    def change_locked_constrained(self, x, z, min_x, max_x):
        angle = math.atan2(self.y.z, math.sqrt(self.y.x ** 2 + self.y.y ** 2))

        if angle + x < min_x: x = min_x - angle
        if angle + x > max_x: x = max_x - angle

        self.rotate(self.x, x)
        self.rotate(vector.z, z)

    def center_on(self, x, y):
        self.p = vector.Vector(x, y, 0)

    def shift(self, x, y):
        xv = vector.Vector(self.x.x, self.x.y, 0).normalize()
        yv = vector.Vector(self.y.x, self.y.y, 0).normalize()
        yv = yv * (1 + math.sin(abs(self.y.z)))
        self.p += xv * x
        self.p += yv * y
