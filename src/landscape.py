import struct
import random
import math
import mesh
from vector import Vector
from timeit import default_timer as tit

class Landscape:
    def __init__(self, w, frames):
        self.w = w
        self.frames = frames

    def get_mesh_vertex(self, x : int, y : int, i):
        """
        1_________2 4
      11|\        /|
        |  \    /  |
        |   0 3    |
        |   9 6    |
        |  /    \  |
        |/________\|
      10 8        7 5
        """
        f = (x >> 7) & 7
        if y < 0: y = 0
        if y > 127: y = 127
        x &= 127
        frame = self.frames[f]
        o = 12 * (x + 128 * y) + i
        return struct.unpack("fff", frame.v[o * 11 * 4 + 0:o * 11 * 4 + 12])

    def get_z(self, x, y, i):
        return self.get_mesh_vertex(x, y, i)[2]

    def get_vertex(self, x, y, i):
        return Vector(*self.get_mesh_vertex(x, y, i))

    def get_height_interpolated(self, px, py):
        tx = math.floor(px)
        ty = math.floor(py)
        x_ = tx + 0.5
        y_ = ty + 0.5
        x = px - x_
        y = py - y_

        # barycentric coordinates
        # p = v1 * g1 + v2 * g2 + v3 * g3, where g1 + g2 + g3 = 1
        # separated:
        # x = x1 * g1 + x2 * g2 + x3 * g3
        # y = y1 * g1 + y2 * g2 + y3 * g3
        # we use x3 = 0, y3 = 0
        # x = x1 * g1 + x2 * g2
        # y = y1 * g1 + y2 * g2
        # therefore
        # g1 * x1 = x - x2 * g2
        # g2 * y2 = y - y1 * g1

        # center is 0/0
        h3 = self.get_z(tx, ty, 0)

        if x > y: # upper right half
            x2 = 0.5
            y2 = -0.5
            h2 = self.get_z(tx, ty, 2)
        else: # lower left half
            x2 = -0.5
            y2 = 0.5
            h2 = self.get_z(tx, ty, 8)

        if x > -y: # lower right half
            x1 = 0.5
            y1 = 0.5
            h1 = self.get_z(tx, ty, 5)
        else: # upper left half
            x1 = -0.5
            y1 = -0.5
            h1 = self.get_z(tx, ty, 1)

        g1 = (y2 * x - x2 * y) / (y2 * x1 - x2 * y1)
        g2 = (y1 * y - y1 * x) / (y2 * x1 - x2 * y1)
        g3 = 1 - g1 - g2

        return h1 * g1 + h2 * g2 + h3 * g3

    def get_normal(self, px, py):
        tx = math.floor(px)
        ty = math.floor(py)
        x_ = tx + 0.5
        y_ = ty + 0.5
        x = px - x_
        y = py - y_

        v0 = self.get_vertex(tx, ty, 0)

        if x > y: # upper right half
            if x > -y: # lower right half
                va = self.get_vertex(tx, ty, 5)
                vb = self.get_vertex(tx, ty, 4)
            else: # upper left half
                va = self.get_vertex(tx, ty, 2)
                vb = self.get_vertex(tx, ty, 1)
        else: # lower left half
            if x > -y: # lower right half
                va = self.get_vertex(tx, ty, 8)
                vb = self.get_vertex(tx, ty, 7)
            else: # upper left half
                va = self.get_vertex(tx, ty, 11)
                vb = self.get_vertex(tx, ty, 10)

        return ((va - v0).cross(vb - v0)).normalize()
