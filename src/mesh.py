import struct
from allegro import *

class MeshMarker:
    pass

class Mesh:
    def __init__(self):
        self.vbuffer = None
        
    def read(self, f):
        self.n = _read_int(f)
        self.stride = _read_int(f)
        self.v = f.read(self.stride * 4 * self.n)
        self.markers = {}
        marker_count = _read_int(f)
        if marker_count:
            for i in range(marker_count):
                m = MeshMarker()
                m.name = _read_string(f)
                m.transform = f.read(128)
                self.markers[m.name] = m

    def vertex_buffer(self, render):
        if not self.vbuffer:
            self.vbuffer = al_create_vertex_buffer(render.decl, self.v,
                self.n, 0)
        return self.vbuffer

def _read_int(f) -> int:
    return struct.unpack("i", f.read(4))[0]

def _read_string(f) -> str:
    n = _read_int(f)
    return f.read(n).decode("utf8")

def read_frames(f) -> list:
    frames = []
    n = _read_int(f)
    for i in range(n):
        mesh = Mesh()
        mesh.read(f)
        frames += [mesh]
    return frames
