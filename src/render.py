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

        self.screen_size_changed(1280, 720)

        t = byref(ALLEGRO_TRANSFORM())
        al_identity_transform(t)
        self.identity_transform = t

    def screen_size_changed(self, w, h):
        self.w = w
        self.h = h

        t = byref(ALLEGRO_TRANSFORM())
        al_identity_transform(t)
        al_orthographic_transform(t, 0, 0, -1.0, w, h, 1)
        self.default_projection = t

        pt = ALLEGRO_TRANSFORM()
        al_identity_transform(pt)

        vw = 36 * w / h
        al_orthographic_transform(pt, -vw, 36, -200.0, vw, -36, 200)
        self.projection = pt

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
uniform int gray;
varying vec4 color;
varying float light;
void main() {
  light = dot(al_user_attr_0, light_direction);
  if (gray == 1) {
    float c = al_color.x * 0.3 + al_color.y * 0.6 + al_color.z * 0.1;
    color = vec4(c, c, c, 1);
  }
  else {
    color = al_color;
  }
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

def render_projection_transform():
    return _render.projection

def render_camera_transform(game):
    camera = game.camera
    ct = ALLEGRO_TRANSFORM()
    al_build_camera_transform(ct,
        camera.p.x, camera.p.y, camera.p.z,
        camera.p.x - camera.z.x, camera.p.y - camera.z.y, camera.p.z - camera.z.z,
        camera.y.x, camera.y.y, camera.y.z)
    z = 2 ** game.zoom
    al_scale_transform_3d(ct, z, z, z)
    return ct

def render_actor_transform(actor):
    c = actor.cam
    at = ALLEGRO_TRANSFORM()
    al_identity_transform(at)
    at.m[0][0] = c.x.x
    at.m[1][0] = c.y.x
    at.m[2][0] = c.z.x
    at.m[0][1] = c.x.y
    at.m[1][1] = c.y.y
    at.m[2][1] = c.z.y
    at.m[0][2] = c.x.z
    at.m[1][2] = c.y.z
    at.m[2][2] = c.z.z
    return at      

def render_grid_actors(game, ct, pt, x, y, w, h):
    for j in range(y, y + h):
        for i in range(x, x + w):
            for a in game.actors.grid[i + j * 8]:
                render_actor(game, a, ct, pt)

def render_actor(game, actor, ct, pt):
    if len(actor.profession) == 5:
        frame = actor.frame_t + (game.t // 4)
        frame %= 8
        if frame > 4: frame = -frame + 5 + 3
        mesh = actor.profession[frame]
    else:
        mesh = actor.profession[0]

    c = actor.cam
    at = render_actor_transform(actor)

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
    s = actor.scale
    al_scale_transform_3d(t, s, s, s)
    al_compose_transform(t, at)
    al_compose_transform(t, ct)

    al_use_transform(t)

    if actor.gray: al_set_shader_int("gray", 1)

    render_mesh(mesh)

    if actor.gray: al_set_shader_int("gray", 0) 

    if not actor.static:
        p = (c_float * 3)(0, 0, 0)
        al_transform_coordinates_3d(t, byref(p, 0), byref(p, 4), byref(p, 8))
        al_transform_coordinates_3d_projective(pt, byref(p, 0), byref(p, 4), byref(p, 8))
        actor.xos = _render.w / 2 + p[0] * _render.w / 2
        actor.yos = _render.h / 2 - p[1] * _render.h / 2

def render_scene(game):
    if not _render.inited: _render.init()
    camera = game.camera
   
    pt = render_projection_transform()
    al_use_projection_transform(pt)

    ct = render_camera_transform(game)
    al_use_transform(ct)

    al_set_render_state(ALLEGRO_DEPTH_TEST, 1)
    al_use_shader(_render.actor_shader)

    l = _render.light_direction
    f = (c_float * 3)(l.x, l.y, l.z)
    al_set_shader_float_vector("light_direction", 3, f, 1)

    for i in range(len(game.river)):
        if game.scroll > i * 128 - 128 and game.scroll < i * 128 + 128 + 128:
            render_mesh(game.river[i])

    for i in range(len(game.river)):
        if game.scroll > i * 128 - 128 and game.scroll < i * 128 + 128 + 128:
            render_grid_actors(game, ct, pt, i * 8, 0, 8, 8)

    #for actor in game.actors:
    #    render_actor(game, actor, ct, pt)

    al_use_shader(None)
    al_use_projection_transform(_render.default_projection)
    al_use_transform(_render.identity_transform)
    al_set_render_state(ALLEGRO_DEPTH_TEST, 0)

def get_2d(pos, pt, ct):
    t = byref(ALLEGRO_TRANSFORM())
    al_identity_transform(t)
    al_compose_transform(t, ct)
    p = (c_float * 3)(pos.x, pos.y, pos.z)
    al_transform_coordinates_3d(t, byref(p, 0), byref(p, 4), byref(p, 8))
    al_transform_coordinates_3d_projective(pt, byref(p, 0), byref(p, 4), byref(p, 8))
    xos = _render.w / 2 + p[0] * _render.w / 2
    yos = _render.h / 2 - p[1] * _render.h / 2
    return xos, yos

def get_reverse_2d(cam, xos, yos, ct):
    w = _render.w
    h = _render.h
    vh = 36
    vw = vh * w / h
    x = (xos - w / 2) * 2 * vw / w
    y = (h / 2 - yos) * 2 * vh / h
    it = ALLEGRO_TRANSFORM()
    al_identity_transform(it)
    for i in range(3):
        for j in range(3):
            it.m[i][j] = ct.m[j][i]
    p = (c_float * 3)(x, y, 0)
    al_transform_coordinates_3d(it, byref(p, 0), byref(p, 4), byref(p, 8))
    rx = cam.p.x + p[0] * 2
    ry = cam.p.y + p[1] * 2
    return rx, ry

def resize(w, h):
    _render.screen_size_changed(w, h)
