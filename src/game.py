from allegro import *
import controls
import mesh
import render
import camera
import math
import random
import actor
import landscape
import vector
from math import pi

_game = None
def get():
    return _game

class Game:
    def __init__(self, path):
        self.path = path
        global _game
        _game = self

        self.input = controls.Input()

        self.font = al_load_font(self.path + "/data/JosefinSans-Regular.ttf", -12, 0)

        self.raft = mesh.read_frames(self.path + "/data/raft.mesh")
        self.river = mesh.read_frames(self.path + "/data/perlin.mesh.gz")
        self.dragon = mesh.read_frames(self.path + "/data/dragon.mesh")

        self.zoom = 0
        self.rotation = 0
        self.scroll = 0
        self.camera = camera.Camera()
        self.rotate_camera(0)
        self.scroll_camera(0)

        self.t = 0

        self.fps = [0, 0, 0, 0, 0, 0]
        self.fps_t = 0

        self.landscape = landscape.Landscape(128, self.river)

        self.actors = actor.Actors()

        self.picked = None

        for i in range(7):
            x = 16
            y = 64
            self.actors.new(self.raft, x, y)

        self.actors.new(self.dragon, -100, 64, flying = True,
            scale = 5, z = 20)

    def rotate_camera(self, amount):
        self.rotation += amount
        if self.rotation < 0: self.rotation = 0
        if self.rotation > pi: self.rotation = pi
        self.camera.unrotate()
        self.camera.rotate(vector.x, 1.3 * math.pi)
        self.camera.rotate(vector.z, self.rotation)
        self.camera.rotate(vector.y, 0.125 * math.pi)

    def scroll_camera(self, amount):
        self.scroll += amount
        self.camera.center_on(self.scroll, 64)

    def draw(self):
        al_clear_to_color(al_map_rgb_f(0, 0, 1))
        al_clear_depth_buffer(1)

        render.render_scene(self)

        pt = render.render_projection_transform()
        ct = render.render_camera_transform(self)

        for a in self.actors:
            
            t = byref(ALLEGRO_TRANSFORM())
            al_identity_transform(t)
            al_compose_transform(t, ct)

            p = (c_float * 3)(a.cam.p.x, a.cam.p.y, a.cam.p.z)
            al_transform_coordinates_3d(t, byref(p, 0), byref(p, 4), byref(p, 8))
            al_transform_coordinates_3d_projective(pt, byref(p, 0), byref(p, 4), byref(p, 8))
            xos0 = 640 + p[0] * 640
            yos0 = 360 - p[1] * 360

            n = a.ground_normal
            s = 10
            p = (c_float * 3)(a.cam.p.x - n.x * s, a.cam.p.y - n.y * s, a.cam.p.z - n.z * s)
            al_transform_coordinates_3d(t, byref(p, 0), byref(p, 4), byref(p, 8))
            al_transform_coordinates_3d_projective(pt, byref(p, 0), byref(p, 4), byref(p, 8))
            xos = 640 + p[0] * 640
            yos = 360 - p[1] * 360

            al_draw_line(xos0, yos0, xos, yos, al_map_rgb_f(1, 0, 0), 1)
            al_draw_line(a.xos, a.yos, a.xos, a.yos - 100, al_map_rgb_f(0, 0, 1), 1)
            
            al_draw_text(self.font, al_map_rgb_f(1, 1, 1), a.xos, a.yos,
                0, "%.1f" % (a.cam.get_heading()))

        self.draw_fps()
        
        al_flip_display()

    def draw_fps(self):
        if self.t >= self.fps_t + 60:
            for i in range(5, 0, -1):
                self.fps[i] = self.fps[i - 1]
            self.fps[0] = 0
            self.fps_t += 60
        self.fps[0] += 1

        al_draw_text(self.font, al_map_rgb_f(0, 0, 0), 0, 0, 0,
            "fps %.1f %.1f, %.1f" % (self.fps[1], sum(self.fps[1:]) / 5,
                self.zoom))

    def tick(self):
        if self.input.mouse_button(1):
            pass

        mx = self.input.mx
        my = self.input.my

        if self.input.mouse_button(2):
            dx = mx.d * -0.005
            dy = my.d * -0.5
            self.rotate_camera(dx)

            self.scroll_camera(dy)
        if self.input.mz.d:
            self.zoom -= self.input.mz.d * 0.1
            if self.zoom < -1: self.zoom = -1
            if self.zoom > 1: self.zoom = 1

        if self.picked:
            picked, px, py, sx, sy = self.picked
            c = self.camera
            ct = ALLEGRO_TRANSFORM()
            al_build_camera_transform(ct,
                0, 0, 0,
                0 - c.z.x, 0 - c.z.y, 0 - c.z.z,
                c.y.x, c.y.y, c.y.z)
            it = ALLEGRO_TRANSFORM()
            al_identity_transform(it)
            for i in range(3):
                for j in range(3):
                    it.m[i][j] = ct.m[j][i]
            x = mx.v - picked.xos + sx - px
            y = my.v - picked.yos + sy - py
            f = (c_float * 3)(x, -y, 0)
            al_transform_coordinates_3d(it, byref(f, 0), byref(f, 4), byref(f, 8))
            d = vector.Vector(f[0], f[1], 0)
            if d.length() > 0.5:
                d = d / d.length() * 0.5
            picked.v += d

        closest = None

        for a in self.actors:
            a.tick(self.actors)

            dx = a.xos - mx.v
            dy = a.yos - my.v
            d = dx * dx + dy * dy
            if closest is None or d < closest[0]:
                closest = d, a

        if self.input.key_released.get(ALLEGRO_KEY_BUTTON_A, False):
            self.picked = None

        if self.input.key_pressed.get(ALLEGRO_KEY_BUTTON_A, False) and closest:
            if closest[0] < 40 * 40:
                self.picked = closest[1], mx.v, my.v, closest[1].xos, closest[1].yos

        self.t += 1

