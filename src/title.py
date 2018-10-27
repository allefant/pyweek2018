import game
import render
import camera
import mesh
import actor
import landscape
from math import *
import vector
from vector import Vector
from allegro import *

story = """
Snow Hill
. PyWeek 10/2018 entry
. by Allefant

Seven mages went for a boat ride.
. But they forgot their boats.
.

:g Let me cast a nature spell
. so trees are growing from the ground
. and we can use the wood for rafts.
!
:w I don't need a raft
. I can just flow down the river
. if I turn it to ice.

!
:r No way!
. I'll melt away your stupid ice
!

:r or paint some of it red at least.
.
:y Why don't we just ride on
. elephants? I'll summon some.
.
!
:y And they are yellow!
.
:p I've had enough!
. I'll call upon my dragon
. to fly me home now.
.
:s Ahhh! I see a dragon in the distance!
. Let me put a curse on it!
.
. wait, I think that made it angry
.
:b This is getting bad...
. I'll cast a flow spell
. to safely guide us down!
.
!
:b Let's flow!

Drag with the right mouse button
. to move/turn the camera.
Drag with the left mouse button
. to control the mage's flow spell.
Nudge the rafts away from the edge
. so all seven wizards flow down
. the snowy hill to safety!
.
!
"""

ending = """
/Game Over
*Game Won
.

:g! That was no fun. I didn't make it.
.
:g* That was fun! And very easy.
.

:r! So unfair.
. There was no way I could have made it.
.
:r* With much skill
. I am among the ones who made it!
.

:s! I hate this game, way too hard.
.
:s* I hate this game, way too easy.
.

:b* Let's do it again!
.
:b! Let's not do this again.
.

:w* Oh what fun it is to ride
. in a one horse open sleigh!
.
:w! I almost made it!
. Let's give it another try!
.

:y* The elephants saved us!
.
:y! All because of that dreaded dragon.
.

:p* I made it, but...
. How do I get my dragon back?
.
.
:p! At least my dragon lives!
.
.


Thanks for playing!
.
. Thanks everyone for a fun week!
.
.
.
.
. See you next pyweek!
.
.
.
.
.
.
.


"""

class Span:
    def __init__(self, text, speaker, color, t_from, t_until):
        self.text = text
        self.speaker = speaker
        self.color = color
        self.t_from = t_from
        self.t_until = t_until
        self.wait = False
        self.special = 0
        self.gone = False

colors = ["silver", "red", "green", "blue", "black", "white", "yellow", "purple"]
speakers = {"r" : 1, "g" : 2, "b" : 3, "s" : 4, "w" : 5, "y" : 6, "p" : 7}
def get_speaker(x):
    return speakers.get(x, 0)

class Title:

    def __init__(self):
        g = game.get()
        self.path = g.path
        self.camera = camera.Camera()
        self.tree = g.pine_p
        self.zoom = 0.1
        self.scroll = 0
        self.camera.center_on(64, 75)
        self.camera.rotate(vector.x, 1.3 * pi)

        self.river = mesh.read_frames(self.path + "/data/title.mesh.gz")
        self.river1 = mesh.read_frames(self.path + "/data/title1.mesh.gz")
        self.river2 = mesh.read_frames(self.path + "/data/title2.mesh.gz")
        self.raft_p = mesh.read_frames(self.path + "/data/raft0.mesh.gz")
        self.elephant_p = mesh.read_frames(self.path + "/data/elefant_yellow.mesh.gz")
        self.landscape = landscape.Landscape(self.river)
        self.actors = actor.Actors(self.landscape)
        self.pos = 0
        self.died = 0

        self.parse_text(story)

        self.mages = []
        for i in range(7):
            a = self.actors.new(g.mage_p[i], 64 + (i - 3.5) * 10, 64)
            a.cam.rotate(vector.z, pi)
            self.mages.append(a)

        self.t = 0
        render.resize(1280, 720)
        self.special = 0

    def parse_text(self, text):
        self.spans = []
        rows = text.strip().splitlines()
        i = 0
        s = 0
        dur = 80
        self.specials = []
        self.special = 0
        for row in rows:
            g = game.get()
            prev = None
            start = s
            speaker = 0
            gone = False
            if row.startswith("/"):
                row = row[1:]
                if self.died < 7: gone = True
            if row.startswith("*"):
                row = row[1:]
                if self.died == 7: gone = True
            if row.startswith(":"):
                speaker = get_speaker(row[1])
                if row[2] == "!":
                    if speaker - 1 in self.dead_colors:
                        row = row[4:]
                    else:
                        gone = True
                elif row[2] == "*":
                    if speaker - 1 not in self.dead_colors:
                        row = row[4:]
                    else:
                        gone = True
                else:
                    row = row[3:]
            if row.startswith("."):
                row = row[1:]
                if row.startswith(" "): row = row[1:]
                prev = self.spans[-1]
                prev.wait = True
                gone = prev.gone
                if not gone:
                    speaker = prev.speaker
                    j = len(self.spans) - 2
                    while prev.wait:
                        prev.t_until = s + dur
                        if j < 0: break
                        prev = self.spans[j]
                        j -= 1
            if row.startswith("!"):
                row = row[1:]
                self.specials.append(start)
            color = colors[speaker]
            if gone:
                row = ""
                s -= dur
            span = Span(row, speaker, color, start, s + dur)
            span.gone = gone
            self.spans.append(span)
            i += 1
            s += dur

    def get_text(self):
        while self.pos < len(self.spans):
            span = self.spans[self.pos]
            if self.t >= span.t_until:
                self.pos += 1
            else:
                break
        if self.pos >= len(self.spans):
            return []

        span = self.spans[self.pos]
        if span.t_from > self.t: return []
        text = [span]
        i = 1
        while self.pos + i < len(self.spans):
            span = self.spans[self.pos + i]
            if span.t_from > self.t: break
            text += [span]
            i += 1
        return text
    
    def draw(self):
        g = game.get()
        render.render_scene(self)

        text = self.get_text()
        row = 1
        for span in text:
            if not span.text: continue
            x = g.dw / 2
            y = 50 * row
            color = al_color_name(span.color)
            w = al_get_text_width(g.font_big, span.text)

            if span.speaker:
                mage = self.mages[span.speaker - 1]
                al_draw_line(mage.xos, mage.yos, x, y, color, 3)

            al_draw_filled_rectangle(x - w / 2, y, x + w / 2, y + 50,
                al_map_rgba_f(0.5, 0.5, 0.5, .9))
            al_draw_text(g.font_big, color,
                x, y, ALLEGRO_ALIGN_CENTRE, span.text)
            
            row += 1

    def tick(self):
        g = game.get()

        if g.input.mouse_button(1) or\
                g.input.key_pressed.get(ALLEGRO_KEY_ENTER, False):
            g.show_title(False)
            return

        if g.input.key_pressed.get(ALLEGRO_KEY_SPACE, False):
            self.t += 80
        
        self.t += 1
        for s in self.specials[self.special:]:
            if self.t >= s:
                self.special += 1
                if self.special == 1:
                    for i in range(7):
                        a = self.actors.new(self.raft_p, 64 + (i - 3.5) * 10, 80, scale = 3)
                if self.special == 2:
                    self.river = self.river1
                if self.special == 3:
                    self.river = self.river2
                if self.special == 4:
                    for i in range(7):
                        a = self.actors.new(self.elephant_p, 64 + (i - 3.5) * 10, 30 + (i % 3) * 5, scale = 3)
                        a.cam.rotate(vector.z, pi + (i - 3.5) * 0.1)
                if self.special == 5:
                    self.actors = actor.Actors(self.landscape)
                    self.mages = []
                    for i in range(7):
                        a = self.actors.new(g.raft_p[i], 64 + (i - 3.5) * 10, 64)
                        a.cam.rotate(vector.z, pi)
                        self.mages.append(a)
                if self.special == 6:
                    g.show_title(False)

    def ending(self):
        g = game.get()
        self.t = 0
        self.died = 0
        self.pos = 0

        self.dead_colors = set()
        for r in g.raft:
            if r.state == actor.GONE:
                self.died += 1
                self.dead_colors.add(r.color_index)

        self.actors = actor.Actors(self.landscape)
        self.mages = []
        for i in range(7):
            a = self.actors.new(g.mage_p[i], 64 + (i - 3.5) * 10, 64)
            a.cam.rotate(vector.z, pi)
            self.mages.append(a)
            if i in self.dead_colors:
                a.gray = 1

        self.parse_text(ending)

