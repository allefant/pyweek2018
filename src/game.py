from allegro import *
import controls

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

        self.t = 0

    def draw(self):
        al_clear_to_color(al_map_rgb_f(0., 0, 0))
        al_flip_display()

    def tick(self):
        self.t += 1
       
