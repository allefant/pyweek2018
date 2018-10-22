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

        for i in range(10):
            x = random.uniform(0, 128)
            y = random.uniform(0, 128)
            self.actors.new(self.raft, x, y)

    def rotate_camera(self, amount):
        self.rotation += amount
        self.camera.unrotate()
        self.camera.rotate(vector.x, 1.125 * math.pi)
        self.camera.rotate(vector.z, self.rotation)
        self.camera.rotate(vector.y, 0.125 * math.pi)

    def scroll_camera(self, amount):
        self.scroll += amount
        self.camera.center_on(self.scroll, 64)

    def draw(self):
        al_clear_to_color(al_map_rgb_f(0, 0, 1))
        al_clear_depth_buffer(1)

        render.render_scene(self)

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
            "fps %.1f %.1f" % (self.fps[1], sum(self.fps[1:]) / 5))

    def tick(self):
        if self.input.mouse_button(1):
            pass

        if self.input.mouse_button(2):
            dx = self.input.mx.d * -0.005
            dy = self.input.my.d * -0.5
            self.rotate_camera(dx)

        self.scroll_camera(0.1)

        if self.input.mz.d:
            self.zoom -= self.input.mz.d * 0.1
            if self.zoom < -2: self.zoom = -2
            if self.zoom > 2: self.zoom = 2

        for a in self.actors:
            a.tick(self.actors)

        self.t += 1
