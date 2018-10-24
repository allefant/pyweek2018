from allegro import *
from ctypes import Structure
from ctypes import c_float
import vector; Vector = vector.Vector
import math
from camera import Camera

class VERTEX(Structure):
    _fields_ = [
    ("x", c_float),
    ("y", c_float),
    ("z", c_float),
    ("nx", c_float),
    ("ny", c_float),
    ("nz", c_float),
    ("color", ALLEGRO_COLOR),
    ("i", c_float)
    ]

class Render:

    def __init__(self):
        self.inited = False

        self.light_direction = Vector(1, 0, 1).normalize()

        t = byref(ALLEGRO_TRANSFORM())
        al_identity_transform(t)
        al_orthographic_transform(t, 0, 0, -1.0, 1280, 720, 1)
        self.default_projection = t

        t = byref(ALLEGRO_TRANSFORM())
        al_identity_transform(t)
        self.identity_transform = t

    def check_log(self, phase):
        s = al_get_shader_log(self.actor_shader)
        if not s: return
        print(phase)
        print(s)

    def init(self):
        elements = (ALLEGRO_VERTEX_ELEMENT * 5)()
        elem(elements[0], ALLEGRO_PRIM_POSITION, ALLEGRO_PRIM_FLOAT_3, 0)
        elem(elements[1], ALLEGRO_PRIM_USER_ATTR + 0, ALLEGRO_PRIM_FLOAT_3, 12)
        elem(elements[2], ALLEGRO_PRIM_COLOR_ATTR, 0, 24)
        elem(elements[3], ALLEGRO_PRIM_USER_ATTR + 1, ALLEGRO_PRIM_FLOAT_1, 40)
        elem(elements[4], 0, 0, 0)
        self.decl = al_create_vertex_decl(elements, 44)

        self.actor_shader = al_create_shader(ALLEGRO_SHADER_GLSL)
        
        al_attach_shader_source(self.actor_shader, ALLEGRO_VERTEX_SHADER, """
attribute vec4 al_pos;
attribute vec4 al_color;
attribute vec3 al_user_attr_0;
uniform mat4 al_projview_matrix;
uniform vec3 light_direction;
varying vec4 color;
varying float light;
void main() {
  light = dot(al_user_attr_0, light_direction);
  color = al_color;
  gl_Position = al_projview_matrix * al_pos;
}
        """)
        self.check_log("Vertex Shader")
        al_attach_shader_source(self.actor_shader, ALLEGRO_PIXEL_SHADER, """
varying vec4 color;
varying float light;
void main() {
  vec4 c = color;
  float l = light;
  if (l > 0.0) l *= 2.0;
  l = (1.0 + light) / 2.0;
  gl_FragColor = vec4(c.xyz * l, c.w);
}
        """)
        self.check_log("Pixel Shader")
        
        al_build_shader(self.actor_shader)
        self.check_log("Shader Compiler")
        
        self.inited = True

_render = Render()

def elem(e, a, b, c):
    e.attribute = a
    e.storage = b
    e.offset = c

def render_mesh(mesh):
    vbuffer = mesh.vertex_buffer(_render)
    al_draw_vertex_buffer(vbuffer, None, 0, mesh.n, ALLEGRO_PRIM_TRIANGLE_LIST)

def render_scene(game):
    if not _render.inited: _render.init()
    camera = game.camera
   
    pt = ALLEGRO_TRANSFORM()
    al_identity_transform(pt)
    al_orthographic_transform(pt, -64, 36, -200.0, 64, -36, 200)
    al_use_projection_transform(pt)

    ct = byref(ALLEGRO_TRANSFORM())
    al_build_camera_transform(ct,
        camera.p.x, camera.p.y, camera.p.z,
        camera.p.x - camera.z.x, camera.p.y - camera.z.y, camera.p.z - camera.z.z,
        camera.y.x, camera.y.y, camera.y.z)
    z = 2 ** game.zoom
    al_scale_transform_3d(ct, z, z, z)
    al_use_transform(ct)

    l = _render.light_direction
    f = (c_float * 3)(l.x, l.y, l.z)
    al_set_shader_float_vector("light_direction", 3, f, 1)

    al_set_render_state(ALLEGRO_DEPTH_TEST, 1)
    al_use_shader(_render.actor_shader)

    render_mesh(game.river[0])
    render_mesh(game.river[1])
    render_mesh(game.river[2])
    render_mesh(game.river[3])
    render_mesh(game.river[4])
    render_mesh(game.river[5])
    render_mesh(game.river[6])
    render_mesh(game.river[7])

    for actor in game.actors:
        frame = actor.frame_t + (game.t // 4)
        frame %= 8
        if frame > 4: frame = -frame + 5 + 3
        mesh = actor.profession[frame]

        c = actor.cam
        at = ALLEGRO_TRANSFORM()
        al_build_camera_transform(at,
            0, 0, 0,
            -c.z.x, -c.z.y, -c.z.z,
            c.y.x, c.y.y, c.y.z)

        it = ALLEGRO_TRANSFORM()
        al_identity_transform(it)
        for i in range(3):
            for j in range(3):
                it.m[i][j] = at.m[j][i]

        l = _render.light_direction
        f = (c_float * 3)(l.x, l.y, l.z)
        al_transform_coordinates_3d(it, byref(f, 0), byref(f, 4), byref(f, 8))
        al_set_shader_float_vector("light_direction", 3, f, 1)
        
        al_translate_transform_3d(at, c.p.x, c.p.y, c.p.z)

        t = byref(ALLEGRO_TRANSFORM())
        al_identity_transform(t)
        s = 2.5
        al_scale_transform_3d(t, s, s, s)
        al_compose_transform(t, at)
        al_compose_transform(t, ct)

        al_use_transform(t)
        render_mesh(mesh)

        p = (c_float * 3)(0, 0, 0)
        al_transform_coordinates_3d(t, byref(p, 0), byref(p, 4), byref(p, 8))
        al_transform_coordinates_3d_projective(pt, byref(p, 0), byref(p, 4), byref(p, 8))
        actor.xos = 640 + p[0] * 640
        actor.yos = 360 - p[1] * 360

    al_use_shader(None)
    al_use_projection_transform(_render.default_projection)
    al_use_transform(_render.identity_transform)
    al_set_render_state(ALLEGRO_DEPTH_TEST, 0)
    
