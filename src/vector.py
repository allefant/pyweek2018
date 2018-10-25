import math

def _vectorize(v):
    if isinstance(v, Vector): return v
    if isinstance(v, tuple):
        if len(v) == 2: return Vector(v[0], v[1], 0)
        return Vector(v[0], v[1], v[2])
    return o

class Vector:
    def __init__(v, x, y, z): v.x, v.y, v.z = x, y, z
    def copy(v): return Vector(v.x, v.y, v.z)

    def __iter__(v):
        return iter([v.x, v.y, v.z])

    def __add__(v, w):
        w = _vectorize(w)
        return Vector(v.x + w.x, v.y + w.y, v.z + w.z)
    def __sub__(v, w):
        w = _vectorize(w)
        return Vector(v.x - w.x, v.y - w.y, v.z - w.z)
    def __matmul__(v, w):
        return Vector(
            v.y * w.z - w.y * v.z,
            v.z * w.x - w.z * v.x,
            v.x * w.y - w.x * v.y)
    def cross(v, w):
        return v.__matmul__(w)

    def __neg__(v):
        return Vector(-v.x, -v.y, -v.z)

    def __mul__(v, w):
        if isinstance(w, Vector): return v.x * w.x + v.y * w.y + v.z * w.z
        return Vector(v.x * w, v.y * w, v.z * w)

    def __rmul__(v, w):
        return Vector(v.x * w, v.y * w, v.z * w) 

    def __truediv__(v, w):
        return Vector(v.x / w, v.y / w, v.z / w)

    def length(v): return math.sqrt(v * v)
    def normalize(v):
        l = v.length()
        return Vector(v.x / l, v.y / l, v.z / l)

    def rotate(v, a, angle):
        """
        Rotate the vector /v/ around axis /a/ by /angle/ in counter clockwise direction.
        If this vector is a point in world space, then the axis of rotation is
        defined by the origin and the a vector.
        """
        c = math.cos(angle)
        s = math.sin(angle)

        r = a * a.x * (1 - c)
        u = a * a.y * (1 - c)
        b = a * a.z * (1 - c)

        r.x += c
        r.y += a.z * s
        r.z -= a.y * s

        u.x -= a.z * s
        u.y += c
        u.z += a.x * s

        b.x += a.y * s
        b.y -= a.x * s
        b.z += c

        return Vector(v * r, v * u, v * b)

    def __str__(self):
        return "%.1f/%.1f/%.1F" % (self.x, self.y, self.z)

o = Vector(0, 0, 0)
x = Vector(1, 0, 0)
y = Vector(0, 1, 0)
z = Vector(0, 0, 1)
