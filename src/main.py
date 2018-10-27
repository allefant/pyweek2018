#!/usr/bin/env python3
from allegro import *
import os
import sys
import game

path = os.getcwd()
if not os.path.exists(path + "/data"):
    path += "/.."

def main():
    #al_install_system(ALLEGRO_VERSION_INT, None)
    # we don't want to fail just because the version is wrong :P
    if not al_install_system(al_get_allegro_version(), None):
        print("Could not install Allegro!")

    al_init_image_addon()
    al_init_font_addon()
    al_init_ttf_addon()
    al_install_keyboard()
    al_install_mouse()
    al_init_primitives_addon()
    al_install_audio()
    al_init_acodec_addon()
    al_reserve_samples(20)
    al_set_mixer_gain(al_get_default_mixer(), 2)
    al_set_new_window_title("Snow Hill by Allefant - PyWeek 2018/10")
    al_set_new_display_flags(ALLEGRO_WINDOWED | ALLEGRO_RESIZABLE |
        ALLEGRO_OPENGL | ALLEGRO_PROGRAMMABLE_PIPELINE)
    al_set_new_display_option(ALLEGRO_DEPTH_SIZE, 16, ALLEGRO_SUGGEST)
    al_set_new_display_option(ALLEGRO_SAMPLE_BUFFERS, 1, ALLEGRO_SUGGEST)
    al_set_new_display_option(ALLEGRO_SAMPLES, 16, ALLEGRO_SUGGEST)
    display = al_create_display(1280, 720)
    if not display:
        print("Could not create display!")

    timer = al_create_timer(1 / 60)

    queue = al_create_event_queue()
    al_register_event_source(queue, al_get_keyboard_event_source())
    al_register_event_source(queue, al_get_mouse_event_source())
    al_register_event_source(queue, al_get_timer_event_source(timer))
    al_register_event_source(queue, al_get_display_event_source(display))

    _game = game.Game(path)

    al_start_timer(timer)

    done = False
    need_redraw = True
    while not done:
        event = ALLEGRO_EVENT()
        if need_redraw and al_is_event_queue_empty(queue):
            _game.draw()
            need_redraw = False

        al_wait_for_event(queue, byref(event))

        if event.type == ALLEGRO_EVENT_KEY_CHAR:
            if event.keyboard.keycode == ALLEGRO_KEY_ESCAPE:
               done = True

        if event.type == ALLEGRO_EVENT_DISPLAY_CLOSE:
            done = True

        if event.type == ALLEGRO_EVENT_TIMER:
            _game.tick()
            _game.input.tick()
            need_redraw = True

        if event.type == ALLEGRO_EVENT_MOUSE_AXES:
            _game.input.set_mouse_position(event.mouse.x, event.mouse.y, event.mouse.z, event.mouse.w)

        if event.type == ALLEGRO_EVENT_MOUSE_BUTTON_DOWN:
            if event.mouse.button == 1: _game.input.add_key_down(ALLEGRO_KEY_BUTTON_A)
            if event.mouse.button == 2: _game.input.add_key_down(ALLEGRO_KEY_BUTTON_B)

        if event.type == ALLEGRO_EVENT_MOUSE_BUTTON_UP:
            if event.mouse.button == 1: _game.input.add_key_up(ALLEGRO_KEY_BUTTON_A)
            if event.mouse.button == 2: _game.input.add_key_up(ALLEGRO_KEY_BUTTON_B)

        if event.type == ALLEGRO_EVENT_KEY_DOWN:
            _game.input.add_key_down(event.keyboard.keycode)

        if event.type == ALLEGRO_EVENT_KEY_UP:
            _game.input.add_key_up(event.keyboard.keycode)

        if event.type == ALLEGRO_EVENT_DISPLAY_RESIZE:
            al_acknowledge_resize(display)
            _game.resize(al_get_display_width(display), al_get_display_height(display))

if __name__ == "__main__":
    al_main(main)
