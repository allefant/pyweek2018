from allegro import *
import controls
import mesh
import render
import camera
import math

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

        self.river = mesh.read_frames(open(self.path + "/data/river.mesh", "rb"))

        self.zoom = 0
        self.camera = camera.Camera()
        self.camera.change_locked_constrained(math.pi + math.pi / 8, 0, -9, 9)

        self.t = 0

    def draw(self):
        al_clear_to_color(al_map_rgb_f(0, 0, 0))
        al_clear_depth_buffer(1)

        render.render_scene(self)
        
        al_flip_display()

    def tick(self):
        if self.input.mouse_button(1):
            dx = self.input.mx.d * 0.01
            dy = self.input.my.d * 0.01
            self.camera.change_locked_constrained(-dy, -dx, math.pi / 16, math.pi / 3)

        if self.input.mouse_button(2):
            dx = self.input.mx.d * 0.1
            dy = self.input.my.d * 0.1
            z = 1.0 / (2 ** self.zoom)
            self.camera.shift(-dx * z, dy * z)

        if self.input.mz.d:
            self.zoom -= self.input.mz.d * 0.1
            if self.zoom < -2: self.zoom = -2
            if self.zoom > 2: self.zoom = 2

        self.t += 1
