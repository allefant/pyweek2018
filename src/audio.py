from allegro import *

music = None
playing = False

def load_music(filename):
    global music
    global playing
    if music:
        al_destroy_audio_stream(music)
    playing = True
    music = al_load_audio_stream(filename, 4, 48000)
    al_attach_audio_stream_to_mixer(music, al_get_default_mixer())
    al_set_audio_stream_playmode(music, ALLEGRO_PLAYMODE_LOOP)

def toggle():
    global playing
    playing = not playing
    al_set_audio_stream_playing(music, playing)

def load(filename):
    return al_load_sample(filename)

def play(sample):
    al_play_sample(sample, 1, 0, 1, ALLEGRO_PLAYMODE_ONCE, None)
