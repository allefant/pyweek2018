edit = False
skip = 0

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
from vector import Vector
import json
import title
import audio

_game = None
def get():
    return _game

class Game:
    def __init__(self, path):
        self.path = path
        global _game
        _game = self

        self.show_title(True)

        self.input = controls.Input()

        self.font = al_load_font(self.path + "/data/JosefinSans-Regular.ttf", -12, 0)
        if not self.font:
            print("Cannot find data")
            sys.exit(1)
        self.font_big = al_load_font(self.path + "/data/JosefinSans-Regular.ttf", -48, 0)

        colors = ["red", "green", "blue", "black", "white", "yellow", "purple"]
        self.mage_p = []
        self.raft_p = []
        for i in range(7):
            self.raft_p.append(mesh.read_frames(self.path + "/data/raft%d.mesh.gz" % (1 + i)))
            self.mage_p.append(mesh.read_frames(self.path + "/data/%s mage_fire_outfit.mesh.gz" % colors[i]))
        self.river = mesh.read_frames(self.path + "/data/perlin.mesh.gz")
        self.dragon_p = mesh.read_frames(self.path + "/data/dragon.mesh.gz")
        self.pine_p = mesh.read_frames(self.path + "/data/pine.mesh.gz")
        self.finish_p = mesh.read_frames(self.path + "/data/finish.mesh.gz")
        self.wolf_p = mesh.read_frames(self.path + "/data/wolf.mesh.gz")

        self.roar = audio.load(self.path + "/data/wumpus dines.ogg")
        self.swoosh = audio.load(self.path + "/data/swoosh.ogg")
        self.yelp = audio.load(self.path + "/data/yelp.ogg")
        self.jingle = audio.load(self.path + "/data/jingle.ogg")
        self.rubber = audio.load(self.path + "/data/rubber.ogg")
        self.growl = audio.load(self.path + "/data/growl.ogg")
        self.chew = audio.load(self.path + "/data/chew.ogg")
        self.dogyelp = audio.load(self.path + "/data/dogyelp.ogg")

        self.zoom = 0
        self.rotation = pi / 4
        self.scroll = 20
        self.camera = camera.Camera()
        self.rotate_camera(0)
        self.paused = False
        self.title = title.Title()
        self.silver = al_color_name("silver")

        self.t = 0
        self.spawn = [(128 * 9 - 30, 10),
            (128 * 10 + 40, 10),
            (128 * 11 + 30, 110),
            (128 * 12 + 0, 10),
            (128 * 13 + 0, 10),
            (128 * 13 + 64, 110),
            (128 * 14 + 0, 10),
            (128 * 14 + 64, 110),
            (128 * 15 + 0, 10)]

        self.fps = [0, 0, 0, 0, 0, 0]
        self.fps_t = 0

        self.landscape = landscape.Landscape(self.river)

        self.actors = actor.Actors(self.landscape)

        with open(self.path + "/data/objects.json", "r") as j:
            self.objects = json.load(j)
            for o in self.objects:
                t = self.actors.new(self.pine_p, o["x"], o["y"], radius = 8, scale = 8, static = True)
                t.cam.rotate(vector.z, random.uniform(-pi, pi))
                t.cam.rotate(vector.y, pi / 8)

        t = self.actors.new(self.finish_p, 128 * 16 - 32, 48, z = 20, scale = 20, static = True)
        t.cam.rotate(vector.z, -pi / 2)
        t.cam.rotate(vector.y, pi / 8)

        self.picked = None

        self.resize(1280, 720)

        self.raft = []
        self.raft_and_wolf = []
        for i in range(7):
            x = 16 + skip
            y = 64
            r = self.actors.new(self.raft_p[i], x, y)
            r.color = al_color_name(colors[i])
            r.color_index = i
            self.raft.append(r)
            self.raft_and_wolf.append(r)

        self.dragon = self.actors.new(self.dragon_p, -100, 64, flying = True,
            scale = 5, z = 20)

        self.scroll_camera(self.scroll)
        self.red = al_color_name("crimson")

        #self.title.ending()

    def rotate_camera(self, amount):
        self.rotation += amount
        if self.rotation < 0: self.rotation = 0
        if self.rotation > pi: self.rotation = pi
        self.camera.unrotate()
        self.camera.rotate(vector.x, 1.3 * math.pi)
        self.camera.rotate(vector.z, self.rotation)
        self.camera.rotate(vector.y, 0.125 * math.pi)

    def get_last(self):
        for raft in self.raft:
            if raft.state == actor.FLOWING: return raft
        return self.raft[-1]

    def scroll_camera(self, amount):
        self.scroll += amount
        last = self.get_last()
        first = self.raft[-1]
        if not edit:
            if self.scroll < last.cam.p.x: self.scroll = last.cam.p.x
            if self.scroll > first.cam.p.x + 64: self.scroll = first.cam.p.x + 64
        self.camera.center_on(self.scroll, 64)

    def draw(self):
        al_clear_to_color(al_map_rgb_f(0.5, 0.5, 0.5))
        al_clear_depth_buffer(1)

        if self.showing_title:
            self.title.draw()
        else:
            self.draw_in_game()

        self.draw_fps()
        al_flip_display()

    def draw_in_game(self):
        render.render_scene(self)

        pt = render.render_projection_transform()
        ct = render.render_camera_transform(self)

        # for a in self.actors:
            
            # xos0, yos0 = render.get_3d(a.cam.p, pt, ct)
            # xosx, yosx = render.get_3d(a.cam.p + a.cam.x * 10, pt, ct)
            # xosy, yosy = render.get_3d(a.cam.p + a.cam.y * 10, pt, ct)
            # xosz, yosz = render.get_3d(a.cam.p + a.cam.z * 10, pt, ct)
            #xos, yos = render.get_3d(a.cam.p - a.ground_normal * 10, pt, ct)

            # al_draw_line(xos0, yos0, xosx, yosx, al_map_rgb_f(1, 0, 0), 1)
            # al_draw_line(xos0, yos0, xosy, yosy, al_map_rgb_f(0, 1, 0), 1)
            # al_draw_line(xos0, yos0, xosz, yosz, al_map_rgb_f(0, 0, 1), 1)
            
            # al_draw_text(self.font, al_map_rgb_f(1, 1, 1), a.xos, a.yos,
                # 0, "%.1f" % (a.cam.p.z))

        for i in range(len(self.raft)):
            b = self.dw / 60
            r = self.raft[i]
            x = b
            y = b + i * b * 2 + b
            danger = False
            gone = r.state != actor.FLOWING
            if not gone:
                if r.cam.p.z < -14: danger = True
                if self.dragon.target is r:
                    if (self.dragon.cam.p - r.cam.p).length() < 50:
                        danger = True
            if r.state == actor.WON: danger = False

            if danger:
                al_draw_filled_circle(x, y, b, al_premul_rgba_f(
                    r.color.r, r.color.g, r.color.b, 0.5 + math.sin(2 * pi * self.t / 30) / 2))
            else:
                al_draw_filled_circle(x, y, b, r.color)

            if r.state == actor.WON:
                for i in range(5):
                    al_draw_line(x, y, x + b * math.cos(2 * pi * i / 5),
                        y + b * math.sin(2 * pi * i / 5), self.silver, 3)
            elif gone:
                al_draw_line(x - b, y - b, x + b, y + b, self.red, 3)
                al_draw_line(x + b, y - b, x - b, y + b, self.red, 3)

            if not self.picked and r.swoosh_t > self.t:
                al_draw_line(r.xos, r.yos,
                    r.xos + r.swoosh_xos * b * 2,
                    r.yos + r.swoosh_yos * b * 2, r.color, 3)

        if self.picked:
            p = self.picked[0]
            al_draw_line(p.xos, p.yos,
                self.input.mx.o, self.input.my.o, p.color, 3)

    def draw_fps(self):
        if self.t >= self.fps_t + 60:
            for i in range(5, 0, -1):
                self.fps[i] = self.fps[i - 1]
            self.fps[0] = 0
            self.fps_t += 60
        self.fps[0] += 1

        al_draw_text(self.font, al_map_rgb_f(0, 0, 0), 0, 0, 0,
            "fps %.1f (%.1f 5s) x=%.0f" % (self.fps[1], sum(self.fps[1:]) / 5,
            self.scroll))

    def find_closest_raft_or_wolf_on_screen(self, x, y):
        closest = None
        for a in self.raft_and_wolf:
            if a.state != actor.FLOWING: continue
            dx = a.xos - x
            dy = a.yos - y
            d = dx * dx + dy * dy
            if closest is None or d < closest[0]:
                closest = d, a
        return closest

    def find_closest_raft_to(self, pos):
        closest = None
        for a in self.raft:
            if a.state != actor.FLOWING: continue
            if a.wolf: continue
            d = a.cam.p - pos
            d = d * d
            if closest is None or d < closest[0]:
                closest = d, a
        return closest

    def tick(self):

        if self.showing_title:
            self.title.tick()
            return

        mx = self.input.mx
        my = self.input.my

        if self.input.mouse_button(2):
            dx = mx.d * -0.005
            dy = my.d * -0.5
            self.rotate_camera(dx)

            self.scroll_camera(dy)
        else:
            last = self.get_last()
            if last.cam.p.x > self.scroll - 20:
                self.scroll_camera(0.3)
            
        if self.input.mz.d:
            self.zoom -= self.input.mz.d * 0.1
            if self.zoom < -1: self.zoom = -1
            if self.zoom > 1: self.zoom = 1

        if self.input.key_pressed.get(ALLEGRO_KEY_P, False):
            self.paused = not self.paused

        if self.input.key_pressed.get(ALLEGRO_KEY_M, False):
            audio.toggle()

        if edit and self.input.key_pressed.get(ALLEGRO_KEY_T, False):
            c = self.camera
            ct = ALLEGRO_TRANSFORM()
            al_build_camera_transform(ct,
                0, 0, 0,
                0 - c.z.x, 0 - c.z.y, 0 - c.z.z,
                c.y.x, c.y.y, c.y.z)
            x, y = render.get_reverse_2d(c, mx.v, my.v, ct)
            self.actors.new(self.pine_p, x, y, radius = 8, scale = 8, static = True)
            o = {"x" : x, "y" : y}
            self.objects.append(o)
            with open(self.path + "/data/objects.json", "w") as j:
                json.dump(self.objects, j, indent = 2)

        if self.paused: return

        first = self.raft[-1]
        if self.spawn and first.cam.p.x + 64 > self.spawn[0][0]:
            sx, sy = self.spawn.pop(0)
            wolf = self.actors.new(self.wolf_p, sx, sy, wolf = True)
            wolf.cam.rotate(vector.z, random.uniform(-pi, pi))
            wolf.color = al_color_name("gray")
            self.raft_and_wolf.append(wolf)
            audio.play(self.growl)

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
            dos = (x * x + y * y) ** 0.5
            if dos > 0.01:
                picked.swoosh = d
                picked.swoosh_t = self.t + 180
                picked.swoosh_xos = x / dos
                picked.swoosh_yos = y / dos

        gone = None
        for a in self.actors:
            a.tick(self.actors)
            if a.state == actor.GONE: gone = a
        if gone:
            self.actors.remove(gone)

        gone = None
        for a in self.raft_and_wolf:
            if a.state == actor.GONE: gone = a
        if gone:
            self.raft_and_wolf.remove(gone)

        self.raft.sort(key = lambda x:x.cam.p.x)

        gone = 0
        for raft in self.raft:
            if raft.state == actor.GONE or raft.state == actor.WON: gone += 1

        if gone == 7:
            self.title.ending()
            self.show_title(True)
            return

        closest = self.find_closest_raft_or_wolf_on_screen(mx.v, my.v)

        dragon_close = self.find_closest_raft_to(self.dragon.cam.p)
        if dragon_close:
            self.dragon.target = dragon_close[1]

        if self.input.key_released.get(ALLEGRO_KEY_BUTTON_A, False):
            if self.picked:
                audio.play(self.swoosh)
            self.picked = None

        r = self.dw / 20
        if self.input.key_pressed.get(ALLEGRO_KEY_BUTTON_A, False) and closest:
            if closest[0] < r * r:
                self.picked = closest[1], mx.v, my.v, closest[1].xos, closest[1].yos
                audio.play(self.rubber)

        self.t += 1

    def show_title(self, yes):
        self.showing_title = yes
        if yes:
            audio.load_music(self.path + "/data/the skye boat song.ogg")
        else:
            audio.load_music(self.path + "/data/sugar plum fairies.ogg")

    def resize(self, w, h):
        self.dw = w
        self.dh = h
        render.resize(w, h)
