from allegro import *

class Position:
    def __init__(self):
        self.v = 0
        self.d = 0
        self.o = 0

    def tick(self):
        self.d = self.v - self.o
        self.o = self.v

class Input:
    def __init__(self):
        self.mx = Position()
        self.my = Position()
        self.mz = Position()
        self.mw = Position()

        self.key_pressed = {}
        self.key_released = {}
        self.key = {}

    def tick(self):
        self.mx.tick()
        self.my.tick()
        self.mz.tick()
        self.mw.tick()
        self.key_pressed = {}
        self.key_released = {}

    def set_mouse_position(self, mx, my, mz, mw):
        self.mx.v = mx
        self.my.v = my
        self.mz.v = mz
        self.mw.v = mw

    def add_key_down(self, key):
        if key in self.key_pressed:
            self.key_pressed[key] += 1
        else:
            self.key_pressed[key] = 1
        self.key[key] = 1

    def add_key_up(self, key):
        self.key_released[key] = 1
        if key in self.key:
            del self.key[key]

    def mouse_button(self, b):
        if b == 1: return self.key.get(ALLEGRO_KEY_BUTTON_A, False)
        if b == 2: return self.key.get(ALLEGRO_KEY_BUTTON_B, False)
        return False
