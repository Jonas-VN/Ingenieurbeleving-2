import warnings
warnings.filterwarnings("ignore")

import math
import numpy as np
import random
import sdl2
import sdl2.ext
import sdl2.sdlttf
from sdl2.sdlmixer import *
from sdl2.ext.compat import byteify
from sdl2 import *
import serial
import time
import platform
from numba import jit

windows = False
if "Windows" == platform.system():
    import screen_brightness_control as sbc
    windows = True

arduino = serial.Serial(port='COM5', baudrate=1000000)
arduino.close()
arduino.open()

response = ""
answer = "w!"
pitch = 0
roll = 0

##############
# Constanten #
##############

BREEDTE = 800
HOOGTE = 600

######################
# Globale variabelen #
######################

# positie van de objecten
p_speler = np.array([2 + 1 / math.sqrt(2), 17 - 1 / math.sqrt(2)])
p_ghost = []
p_portal = []

# richting waarin de speler kijkt
r_speler = np.array([1 / math.sqrt(2), -1 / math.sqrt(2)])

# cameravlak
r_cameravlak = np.array([-1 / math.sqrt(2), -1 / math.sqrt(2)])

# wordt op True gezet als het spel afgesloten moet worden
moet_afsluiten = False
possibleSpawns = []
# Settings
text = None
score = 0
lifes = 3
counter = 4
soundSpeed = 1
snelheid = 1.2
sensitivity = 100
y_offset = 0
end_game = False
p_deur = [17, 12]
paused = False
won = False
gameOver = False
tab = 0
begin = True
FOV = 90
d_camera = 1
sprint = False


"""
0: open ruimte
1: muur
2: buiten de wereld
3: gem
4: mogelijke spawn locatie voor de ghost
5: spike
6: portal
"""
# world_map = np.array(
#     [[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
#      [2, 0, 3, 5, 0, 0, 3, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 0, 0, 5, 0, 3, 2],
#      [2, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 1, 1, 1, 0, 2],
#      [2, 3, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 4, 0, 5, 3, 0, 0, 0, 0, 3, 0, 5, 3, 0, 0, 3, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 2],
#      [2, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 3, 0, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 3, 0, 5, 0, 3, 0, 0, 3, 0, 0, 3, 2],
#      [2, 0, 1, 1, 1, 1, 3, 0, 0, 0, 3, 0, 0, 1, 0, 3, 0, 0, 3, 0, 0, 1, 0, 0, 3, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2],
#      [2, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 3, 1, 1, 1, 1, 3, 1, 1, 1, 1, 3, 1, 1, 1, 1, 3, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2],
#      [2, 0, 0, 3, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2],
#      [2, 3, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 0, 1, 0, 3, 0, 0, 3, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 2],
#      [2, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 3, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 3, 0, 4, 5, 0, 0, 3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2],
#      [2, 0, 1, 1, 1, 1, 0, 1, 1, 3, 1, 1, 1, 1, 3, 1, 0, 6, 0, 1, 3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2],
#      [2, 3, 1, 1, 1, 1, 3, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 3, 0, 3, 0, 0, 0, 3, 1, 0, 0, 3, 0, 2],
#      [2, 0, 0, 5, 3, 0, 0, 3, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 2],
#      [2, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 3, 0, 0, 0, 0, 3, 0, 1, 3, 0, 0, 0, 0, 3, 0, 1, 0, 0, 0, 0, 3, 0, 4, 1, 1, 1, 1, 3, 2],
#      [2, 3, 0, 0, 3, 1, 0, 3, 0, 0, 0, 0, 4, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 3, 1, 1, 0, 1, 3, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 2],
#      [2, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 3, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 3, 1, 0, 0, 3, 0, 0, 0, 0, 1, 1, 1, 1, 0, 2],
#      [2, 3, 0, 3, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 3, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 3, 0, 0, 0, 0, 3, 2],
#      [2, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 3, 0, 0, 0, 0, 5, 3, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2],
#      [2, 0, 0, 0, 0, 1, 3, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 0, 1, 0, 1, 3, 1, 0, 1, 1, 1, 1, 1, 2],
#      [2, 3, 0, 0, 3, 1, 0, 0, 0, 1, 1, 1, 0, 3, 0, 0, 0, 3, 0, 0, 0, 0, 3, 1, 1, 1, 1, 1, 0, 1, 3, 0, 0, 3, 0, 0, 0, 1, 1, 1, 1, 1, 2],
#      [2, 1, 1, 1, 1, 1, 1, 1, 3, 0, 0, 0, 3, 1, 1, 1, 1, 1, 1, 3, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 3, 0, 1, 1, 1, 1, 2],
#      [2, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 2],
#      [2, 0, 3, 0, 0, 0, 0, 3, 0, 1, 1, 0, 0, 3, 0, 0, 5, 0, 3, 0, 0, 0, 3, 0, 4, 0, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 3, 2],
#      [2, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 2],
#      [2, 0, 1, 1, 1, 3, 1, 1, 0, 3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 0, 3, 1, 1, 0, 1, 1, 1, 0, 2],
#      [2, 0, 0, 3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 3, 0, 5, 0, 3, 0, 0, 0, 1, 1, 3, 0, 0, 0, 3, 2],
#      [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]
# )


# Vereenvoudigde map voor tijdens de presentatie
world_map = np.array(
    [[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
     [2, 0, 0, 5, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 5, 0, 0, 2],
     [2, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 1, 1, 1, 0, 2],
     [2, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 4, 0, 5, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 2],
     [2, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 2],
     [2, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2],
     [2, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2],
     [2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2],
     [2, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2],
     [2, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 4, 5, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2],
     [2, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 6, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2],
     [2, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2],
     [2, 0, 0, 5, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 2],
     [2, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 4, 1, 1, 1, 1, 0, 2],
     [2, 5, 0, 0, 3, 1, 3, 0, 0, 0, 3, 0, 4, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 2],
     [2, 5, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 3, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 2],
     [2, 5, 0, 0, 3, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 2],
     [2, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 3, 0, 0, 0, 3, 0, 0, 5, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2],
     [2, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 2],
     [2, 0, 0, 0, 3, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2],
     [2, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 2],
     [2, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 2],
     [2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 4, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 2],
     [2, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 2],
     [2, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 2],
     [2, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 2],
     [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]
)

# Vooraf gedefinieerde kleuren
kleuren = [
    sdl2.ext.Color(0, 0, 0),  # 0 = Zwart
    sdl2.ext.Color(255, 0, 0),  # 1 = Rood
    sdl2.ext.Color(200, 0, 0),  # 2 = Donkerder rood
    sdl2.ext.Color(0, 255, 0),  # 3 = Groen
    sdl2.ext.Color(0, 0, 255),  # 4 = Blauw
    sdl2.ext.Color(18, 18, 18),  # 5 = Donker grijs
    sdl2.ext.Color(128, 128, 128),  # 6 = Grijs
    sdl2.ext.Color(192, 192, 192),  # 7 = Licht grijs
    sdl2.ext.Color(255, 255, 255),  # 8 = Wit
]

# Audio
if SDL_Init(SDL_INIT_AUDIO) != 0:
    raise RuntimeError("Cannot initialize audio system: {}".format(SDL_GetError()))

if Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, 2, 1024):
    raise RuntimeError("Cannot open mixed audio: {}".format(Mix_GetError()))

sound_file = sdl2.ext.Resources(__file__, "src").get_path("wood01.ogg")
sound_file2 = sdl2.ext.Resources(__file__, "src").get_path("gem.aif")
sound_file3 = sdl2.ext.Resources(__file__, "src").get_path("Forgoten_tombs.mp3")
sound_file4 = sdl2.ext.Resources(__file__, "src").get_path("oof.mp3")
sound_file5 = sdl2.ext.Resources(__file__, "src").get_path("spike.mp3")
sound_file6 = sdl2.ext.Resources(__file__, "src").get_path("newscream.mp3")

gemPickup = Mix_LoadWAV(byteify(sound_file2, "utf-8"))
sample = Mix_LoadWAV(byteify(sound_file, "utf-8"))
music = Mix_LoadWAV(byteify(sound_file3, "utf-8"))
oof = Mix_LoadWAV(byteify(sound_file4, "utf-8"))
spike_sound = Mix_LoadWAV(byteify(sound_file5, "utf-8"))
scream = Mix_LoadWAV(byteify(sound_file6, "utf-8"))

channel = Mix_PlayChannel(-1, music, -2)
Mix_Volume(channel, 10)


#####################################################################################################################
# Info: Verwerkt alle input van de controller.                                                                      #
# Input: /                                                                                                          #
# Output: /                                                                                                         #
#####################################################################################################################

def get_data_from_arduino():
    global pitch, roll
    start = False
    data = ""

    for letter in response:
        if letter == "]":
            start = False
            if data:
                data = data.split("/")
                roll = float(data[0])
                pitch = float(data[1])
        elif start:
            data += letter
        elif letter == "[":
            data = ""
            start = True

    if windows:
        start = False
        data = ""
        MAX_BRIGHTNESS = 471.85

        for letter in response:
            if letter == "}":
                start = False
                if data:
                    sbc.set_brightness(int(float(data) / MAX_BRIGHTNESS * 50) + 50)
            if start:
                data += letter
            if letter == "{":
                data = ""
                start = True


#####################################################################################################################
# Info: Verwerkt alle input van het toetsenbord en de muis.                                                         #
# Input: delta (Tijd in milliseconden sinds de vorige oproep van deze functie)                                      #
# Output: /                                                                                                         #
#####################################################################################################################

def verwerk_input(delta):
    global moet_afsluiten
    global p_speler
    global r_speler
    global r_cameravlak
    global y_offset
    global sample
    global counter
    global soundSpeed
    global paused
    global FOV
    global tab
    global sensitivity
    global begin
    global arduino
    global response
    global answer
    global pitch, roll
    global sprint

    get_data_from_arduino()

    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            moet_afsluiten = True
            continue

        # elif event.type == sdl2.SDL_MOUSEWHEEL and paused:
        #    if tab % 2 == 0:
        #        FOV += event.wheel.y
        #    if tab % 2 == 1:
        #        sensitivity += event.wheel.y

    if not paused:
        # Roteren rond as
        alfa = - math.atan(((roll) / 1500 * -sensitivity) / d_camera)
        rotatiematrix = np.array([[math.cos(alfa), -math.sin(alfa)], [math.sin(alfa), math.cos(alfa)]])
        r_speler = np.dot(rotatiematrix, r_speler)
        r_cameravlak = np.dot(rotatiematrix, r_cameravlak)
        # Naar boven en beneden kijken
        if -HOOGTE / 2 < y_offset + pitch * sensitivity < HOOGTE / 2:
            y_offset += pitch * sensitivity

    key_states = sdl2.SDL_GetKeyboardState(None)
    delta *= snelheid
    soundSpeed = 1

    # Als in pauze scherm
    if paused:
        # if key_states[sdl2.SDL_SCANCODE_C]:
        if 'z' in response:
            paused = False
            answer += "u"
        # if key_states[sdl2.SDL_SCANCODE_TAB]:
        if 's' in response:
            tab += 1

        if 'q' in response:
            if tab % 2 == 0 and FOV > 1:
                FOV -= 1
            if tab % 2 == 1:
                sensitivity -= 1
        if 'd' in response:
            if tab % 2 == 0:
                FOV += 1
            if tab % 2 == 1:
                sensitivity += 1

    # Als in begin scherm
    elif begin:
        # if key_states[sdl2.SDL_SCANCODE_S]:
        if 'z' in response:
            begin = False

    # Main game loop handeling
    else:
        # if key_states[sdl2.SDL_SCANCODE_P]:
        if 'p' in response:
            paused = True
            answer += "m"
            tab = 0

        # Sprint
        # if key_states[sdl2.SDL_SCANCODE_LSHIFT] or key_states[sdl2.SDL_SCANCODE_RSHIFT]:
        if 'a' in response:
            sprint = True
            delta *= 2
            soundSpeed = 2
        else:
            sprint = False

        # Vooruit lopen
        # if key_states[sdl2.SDL_SCANCODE_UP] or key_states[sdl2.SDL_SCANCODE_W]:
        if 'z' in response:
            if counter > int(18 / soundSpeed):
                counter = 0
                Mix_PlayChannel(-1, sample, 0)

            if not 0 < world_map[int(p_speler[1])][int(p_speler[0] + r_speler[0] * delta)] <= 2:
                p_speler[0] += r_speler[0] * delta
                if not key_states[sdl2.SDL_SCANCODE_S]:
                    counter += 1

            if not 0 < world_map[int(p_speler[1] + r_speler[1] * delta)][int(p_speler[0])] <= 2:
                p_speler[1] += r_speler[1] * delta
                if not key_states[sdl2.SDL_SCANCODE_S]:
                    counter += 1

        # Achteruit lopen
        # if key_states[sdl2.SDL_SCANCODE_DOWN] or key_states[sdl2.SDL_SCANCODE_S]:
        if 's' in response:
            if counter > int(18 / soundSpeed) and not key_states[sdl2.SDL_SCANCODE_W]:
                counter = 0
                Mix_PlayChannel(-1, sample, 0)

            if not 0 < world_map[int(p_speler[1])][int(p_speler[0] - r_speler[0] * delta)] <= 2:
                p_speler[0] -= r_speler[0] * delta
                if not key_states[sdl2.SDL_SCANCODE_W]:
                    counter += 1

            if not 0 < world_map[int(p_speler[1] - r_speler[1] * delta)][int(p_speler[0])] <= 2:
                p_speler[1] -= r_speler[1] * delta
                if not key_states[sdl2.SDL_SCANCODE_W]:
                    counter += 1

        # Rechts lopen
        # if key_states[sdl2.SDL_SCANCODE_RIGHT] or key_states[sdl2.SDL_SCANCODE_D]:
        if 'd' in response:
            if counter > int(18 / soundSpeed) and not key_states[sdl2.SDL_SCANCODE_S] and not \
                    key_states[sdl2.SDL_SCANCODE_W] and not key_states[sdl2.SDL_SCANCODE_A]:
                counter = 0
                Mix_PlayChannel(-1, sample, 0)

            if not 0 < world_map[int(p_speler[1] + delta * r_cameravlak[1])][int(p_speler[0])] <= 2:
                p_speler[1] += delta * r_cameravlak[1]
                if not key_states[sdl2.SDL_SCANCODE_S] and not key_states[sdl2.SDL_SCANCODE_W] and not \
                        key_states[sdl2.SDL_SCANCODE_A]:
                    counter += 1

            if not 0 < world_map[int(p_speler[1])][int(p_speler[0] + delta * r_cameravlak[0])] <= 2:
                p_speler[0] += delta * r_cameravlak[0]
                if not key_states[sdl2.SDL_SCANCODE_S] and not key_states[sdl2.SDL_SCANCODE_W] and not \
                        key_states[sdl2.SDL_SCANCODE_A]:
                    counter += 1

        # Links lopen
        # if key_states[sdl2.SDL_SCANCODE_LEFT] or key_states[sdl2.SDL_SCANCODE_A]:
        if 'q' in response:
            if counter > int(18 / soundSpeed) and not key_states[sdl2.SDL_SCANCODE_S] and not \
                    key_states[sdl2.SDL_SCANCODE_W] and not key_states[sdl2.SDL_SCANCODE_D]:
                counter = 0
                Mix_PlayChannel(-1, sample, 0)

            if not 0 < world_map[int(p_speler[1] - delta * r_cameravlak[1])][int(p_speler[0])] <= 2:
                p_speler[1] -= delta * r_cameravlak[1]
                if not key_states[sdl2.SDL_SCANCODE_S] and not key_states[sdl2.SDL_SCANCODE_W] and not \
                        key_states[sdl2.SDL_SCANCODE_D]:
                    counter += 1

            if not 0 < world_map[int(p_speler[1])][int(p_speler[0] - delta * r_cameravlak[0])] <= 2:
                p_speler[0] -= delta * r_cameravlak[0]
                if not key_states[sdl2.SDL_SCANCODE_S] and not key_states[sdl2.SDL_SCANCODE_W] and not \
                        key_states[sdl2.SDL_SCANCODE_D]:
                    counter += 1

    if key_states[sdl2.SDL_SCANCODE_ESCAPE]:
        moet_afsluiten = True

    return


#####################################################################################################################
# Info: Berekend de richting van de huidige straal voor een bepaald kolom.                                          #
# Input: r_speler, kolom, r_cameravlak, d_camera                                                                    #
# Output: r_straal                                                                                                  #
#####################################################################################################################

@jit(nopython=True, cache=True)
def bereken_r_straal(r_speler, kolom, r_cameravlak, d_camera):
    r_straal_kolom = d_camera * r_speler + (-1 + (2 * kolom / BREEDTE)) * r_cameravlak
    r_straal = r_straal_kolom / np.linalg.norm(r_straal_kolom)
    return r_straal


#####################################################################################################################
# Info: berekend de afstand tot een muur in de world map en de x-coördinaat in de texture voor op de muur.          #
# Input: p_speler, r_straal, texture_size, world_map, r_speler                                                      #
# Output: d_muur, textuur_x                                                                                         #
#####################################################################################################################

@jit(nopython=True, cache=True)
def raycast(p_speler, r_straal, texture_size, world_map, r_speler):
    x = 0
    y = 0
    delta_v = abs(1 / r_straal[0])
    delta_h = abs(1 / r_straal[1])
    d_muur = 0
    textuur_x = 0

    if r_straal[0] < 0:
        d_verticaal = (p_speler[0] - int(p_speler[0])) * delta_v
    else:
        d_verticaal = (int(p_speler[0]) + 1 - p_speler[0]) * delta_v

    if r_straal[1] < 0:
        d_horizontaal = (p_speler[1] - int(p_speler[1])) * delta_h
    else:
        d_horizontaal = (int(p_speler[1]) + 1 - p_speler[1]) * delta_h

    muur_geraakt = False
    while not muur_geraakt:
        if d_verticaal + y * delta_v < d_horizontaal + x * delta_h:
            i_verticaal = (d_verticaal + y * delta_v) * r_straal + p_speler

            if r_straal[0] < 0:
                if 0 < world_map[int(i_verticaal[1])][round(i_verticaal[0]) - 1] <= 2:
                    d_muur = (d_verticaal + y * delta_v) * np.dot(r_speler, r_straal)
                    textuur_afstand = i_verticaal[1] - int(i_verticaal[1])
                    textuur_x = round(textuur_afstand * texture_size)
                    muur_geraakt = True

            # Hoeft niet te checken voor r_straal, is sws >= 0
            elif 0 < world_map[int(i_verticaal[1])][round(i_verticaal[0])] <= 2:
                d_muur = (d_verticaal + y * delta_v) * np.dot(r_speler, r_straal)
                textuur_afstand = i_verticaal[1] - int(i_verticaal[1])
                textuur_x = round(textuur_afstand * texture_size)
                muur_geraakt = True
            y += 1

        else:
            i_horizontaal = (d_horizontaal + x * delta_h) * r_straal + p_speler

            if r_straal[1] < 0:
                if 0 < world_map[round(i_horizontaal[1]) - 1][int(i_horizontaal[0])] <= 2:
                    d_muur = (d_horizontaal + x * delta_h) * np.dot(r_speler, r_straal)
                    textuur_afstand = i_horizontaal[0] - int(i_horizontaal[0])
                    textuur_x = round(textuur_afstand * texture_size)
                    muur_geraakt = True

            # Hoeft niet te checken voor r_straal, is sws >= 0
            elif 0 < world_map[round(i_horizontaal[1])][int(i_horizontaal[0])] <= 2:
                d_muur = (d_horizontaal + x * delta_h) * np.dot(r_speler, r_straal)
                textuur_afstand = i_horizontaal[0] - int(i_horizontaal[0])
                textuur_x = round(textuur_afstand * texture_size)
                muur_geraakt = True
            x += 1
    return d_muur, textuur_x


#####################################################################################################################
# Info: Rendert één kolom op het scherm, inclusief de luchttexture, muur en de distance fog.                        #
# Input: texture, sprites_image, renderer, window, kolom, d_muur, textuur_x                                         #
# Output: /                                                                                                         #
#####################################################################################################################

def render_kolom(texture, sprites_image, renderer, window, kolom, d_muur, textuur_x):
    global y_offset
    lengte = 1 / d_muur * window.size[1]
    draw_offset = (window.size[1] - lengte) / 2 + y_offset

    # Lucht
    renderer.copy(sprites_image[0], srcrect=(int(kolom / window.size[0] * sprites_image[0].size[0]), 0, 1,
                                             int(draw_offset / window.size[1] * sprites_image[0].size[1])),
                  dstrect=(kolom, 0, 1, int(draw_offset)))

    # Muren
    renderer.copy(texture, srcrect=(textuur_x, 0, 1, texture.size[1]),
                  dstrect=(kolom, round(draw_offset), 1, round(lengte)))

    # Fog
    color = max(255 - int(d_muur * 25), 0)
    renderer.draw_line((kolom, int(draw_offset), kolom, int(window.size[1] / 2 + draw_offset)),
                       sdl2.ext.Color(color, color, color))

    return


#####################################################################################################################
# Info: Rendert één sprite met een bepaalde grootte ifv de soort sprite                                             #
# Input: sprites_image, sprite, p_speler, renderer, window, z_buffer, (spike)                                       #
# Output: /                                                                                                         #
#####################################################################################################################

def render_sprite(sprites_image, sprite, p_speler, renderer, window, z_buffer, spike=None):
    global y_offset
    global d_camera
    global p_portal

    u, v = np.dot(np.linalg.inv([[r_cameravlak[0], r_speler[0]], [r_cameravlak[1], r_speler[1]]]), sprite - p_speler)
    alfa = u * d_camera / v

    if str(sprite) == str(p_portal):
        scale = 1
        breedte = 0.5 / v * window.size[0]

    elif str(sprite) == str(p_ghost):
        scale = 0.5
        breedte = 0.25 / v * window.size[0]

    elif str(sprite) == str(spike):
        scale = 1
        breedte = 0.6 / v * window.size[0]

    else:
        scale = 0.25
        breedte = scale / v * window.size[0]

    if -1 - breedte / window.size[0] < alfa < 1 + breedte / window.size[0] and v > 0:
        hoogte = scale / v * window.size[1]
        draw_offset_y = (window.size[1] - hoogte) / 2 + y_offset
        draw_offset_x = (window.size[0] + alfa * window.size[0] - breedte) / 2
        delta = sprites_image.size[0] / breedte
        textuur_x = 0

        for kolom in range(int(draw_offset_x), int(draw_offset_x + breedte)):
            if kolom >= window.size[0] - 1:
                kolom = window.size[0] - 2

            try:
                if z_buffer[kolom] > v:
                    z_buffer[kolom] = v
                    renderer.copy(sprites_image, srcrect=(int(textuur_x), 0, 1, sprites_image.size[1]),
                                  dstrect=(kolom, int(draw_offset_y), 1, int(hoogte)))
                textuur_x += delta
            except IndexError:
                pass
                # print("Error: z_buffer")

    return


#####################################################################################################################
# Info: Rendert alle statische elementen zoals de minimap en tekst                                                  #
# Input: renderer, p_speler, sprites_image, sprites, text, textInfo, window, p_ghost                                #
# Output: /                                                                                                         #
#####################################################################################################################

def render_static(renderer, p_speler, minimap, sprites, text, textInfo, text_sprint, window):
    global p_ghost
    scale = 5
    offset_y = window.size[1] - minimap.size[1] * scale

    # Minimap
    renderer.copy(minimap, srcrect=(0, 0, minimap.size[0], minimap.size[1]),
                  dstrect=(0, offset_y, minimap.size[0] * scale, minimap.size[1] * scale))

    # Sprites op minimap
    for sprite in sprites:
        start = int(minimap.size[0] - sprite[0]) * scale
        for x in range(start, start + scale):
            renderer.draw_line((x, int(sprite[1]) * scale + offset_y, x, int(sprite[1]) * scale + scale + offset_y),
                               kleuren[3])

    # Speler op minimap
    start = int(minimap.size[0] - p_speler[0]) * scale
    for x in range(start, start + scale):
        renderer.draw_line((x, int(p_speler[1]) * scale + offset_y, x, int(p_speler[1]) * scale + scale + offset_y),
                           kleuren[4])

    # Ghost op minimap (enkel voor presentatie)
    start = int(minimap.size[0] - p_ghost[0]) * scale
    for x in range(start, start + scale):
        renderer.draw_line((x, int(p_ghost[1]) * scale + offset_y, x, int(p_ghost[1]) * scale + scale + offset_y),
                           kleuren[4])

    # Tekst FPS en levens
    renderer.copy(text, dstrect=(int(window.size[0] / 2) + 75, 20, text.size[0], text.size[1]))

    # Tekst linksboven
    renderer.copy(textInfo, dstrect=(20, 20, textInfo.size[0], textInfo.size[1]))

    # Sprint tekst
    renderer.copy(text_sprint, dstrect=(window.size[0] - text_sprint.size[0], window.size[1] - text_sprint.size[1], text_sprint.size[0], text_sprint.size[1]))

    return


#####################################################################################################################
# Info: Berekent een nieuwe positie voor de ghost                                                                   #
# Input: p_ghost, possibleDirections, ghostDirection, moveCounter                                                   #
# Output: p_ghost, possibleDirections, ghostDirection, moveCounter                                                  #
#####################################################################################################################

def ghost_movement(p_ghost, possibleDirections, ghostDirection, moveCounter, delta):
    global possibleSpawns
    moveCounter += 1
    speed = 0.5 / delta
    step = 1 / speed

    if moveCounter >= speed:
        # Veiligheid voor als er toch een afrondingsfout zou inzitten
        p_ghost = [int(p_ghost[0]) + 0.5, int(p_ghost[1]) + 0.5]

        # Movement of ghost
        if not 0 < world_map[int(p_ghost[1])][int(p_ghost[0] - 1)] <= 2:
            if ghostDirection != "U" and p_speler[0] < p_ghost[0] and "D" not in possibleDirections:
                possibleDirections.append("D")

        if not 0 < world_map[int(p_ghost[1] + 1)][int(p_ghost[0])] <= 2:
            if ghostDirection != "L" and p_speler[1] > p_ghost[1] and "R" not in possibleDirections:
                possibleDirections.append("R")

        if not 0 < world_map[int(p_ghost[1] - 1)][int(p_ghost[0])] <= 2:
            if ghostDirection != "R" and p_speler[1] < p_ghost[1] and "L" not in possibleDirections:
                possibleDirections.append("L")

        if not 0 < world_map[int(p_ghost[1])][int(p_ghost[0] + 1)] <= 2:
            if ghostDirection != "D" and p_speler[0] > p_ghost[0] and "U" not in possibleDirections:
                possibleDirections.append("U")

        k = random.randint(0, 1)
        try:
            if len(possibleDirections) > 1:
                if ghostDirection == "R" or ghostDirection == "L" and p_ghost[0] % 0.5 == 0:
                    randomDir = possibleDirections[k]

                elif ghostDirection == "U" or ghostDirection == "D" and p_ghost[1] % 0.5 == 0:
                    randomDir = possibleDirections[k]

            else:
                if ghostDirection == "R" or ghostDirection == "L" and p_ghost[0] % 0.5 == 0:
                    randomDir = possibleDirections[0]

                elif ghostDirection == "U" or ghostDirection == "D" and p_ghost[1] % 0.5 == 0:
                    randomDir = possibleDirections[0]

        except IndexError:
            if not 0 < world_map[int(p_ghost[1])][int(p_ghost[0] - 1)] <= 2:
                if ghostDirection != "U" and p_speler[0] > p_ghost[0] and "D" not in possibleDirections:
                    possibleDirections.append("D")

            if not 0 < world_map[int(p_ghost[1] + 1)][int(p_ghost[0])] <= 2:
                if ghostDirection != "L" and p_speler[1] < p_ghost[1] and "R" not in possibleDirections:
                    possibleDirections.append("R")

            if not 0 < world_map[int(p_ghost[1] - 1)][int(p_ghost[0])] <= 2:
                if ghostDirection != "R" and p_speler[1] > p_ghost[1] and "L" not in possibleDirections:
                    possibleDirections.append("L")

            if not 0 < world_map[int(p_ghost[1])][int(p_ghost[0] + 1)] <= 2:
                if ghostDirection != "D" and p_speler[0] < p_ghost[0] and "U" not in possibleDirections:
                    possibleDirections.append("U")

            k = random.randint(0, 1)
            try:
                if len(possibleDirections) > 1:
                    if ghostDirection == "R" or ghostDirection == "L" and p_ghost[0] % 0.5 == 0:
                        randomDir = possibleDirections[k]

                    elif ghostDirection == "U" or ghostDirection == "D" and p_ghost[1] % 0.5 == 0:
                        randomDir = possibleDirections[k]

                else:
                    if ghostDirection == "R" or ghostDirection == "L" and p_ghost[0] % 0.5 == 0:
                        randomDir = possibleDirections[0]

                    elif ghostDirection == "U" or ghostDirection == "D" and p_ghost[1] % 0.5 == 0:
                        randomDir = possibleDirections[0]

            except IndexError:
                pass
                # print("Ghost Error")

        if randomDir == "U":
            p_ghost[0] += step
            ghostDirection = "U"
            possibleDirections = []
            moveCounter = 0

        elif randomDir == "D":
            p_ghost[0] -= step
            ghostDirection = "D"
            possibleDirections = []
            moveCounter = 0

        elif randomDir == "R":
            p_ghost[1] += step
            ghostDirection = "R"
            possibleDirections = []
            moveCounter = 0

        elif randomDir == "L":
            p_ghost[1] -= step
            ghostDirection = "L"
            possibleDirections = []
            moveCounter = 0
    else:
        if ghostDirection == "U":
            p_ghost[0] += step

        elif ghostDirection == "D":
            p_ghost[0] -= step

        elif ghostDirection == "R":
            p_ghost[1] += step

        elif ghostDirection == "L":
            p_ghost[1] -= step

    return p_ghost, possibleDirections, ghostDirection, moveCounter


#####################################################################################################################
# Info: Main function, runs the game                                                                                #
# Input: /                                                                                                          #
# Output: /                                                                                                         #
#####################################################################################################################

def main():
    # ---> Globale variabelen <--- #
    global score
    global lifes
    global p_ghost
    global or_p_ghost
    global paused
    global FOV
    global d_camera
    global tab
    global won
    global gameOver
    global p_portal
    global begin
    global response
    global answer
    global possibleSpawns
    global sprint
    global sensitivity
    global world_map

    # ---> Variabelen initialiseren <--- #
    paused = False
    spikes_animation = False
    spikes_count = -2.24
    delta = 1
    ghostDirection = "D"
    possibleDirections = []
    moveCounter = 0
    jumpscare = False
    jumpscareCount = 0
    jumpscareLength = 20
    blood = False
    bloodCount = 0
    bloodLength = 20
    startCount = 0

    # ---> Positie van alle belangrijke elementen berekenen uit de world_map <--- #
    sprites = []
    spikes = []
    possibleSpawns = []

    # Zoekt alle sprites (getallen hoger dan 2 in de world_map) en append deze aan de sprites array
    for y in range(len(world_map)):
        for x in range(len(world_map[y])):
            # gems
            if world_map[y][x] == 3:
                sprites.append([x + 0.5, y + 0.5])

            # ghost
            if world_map[y][x] == 4:
                p_ghost = [x + 0.5, y + 0.5]
                possibleSpawns.append(p_ghost)

            # spikes
            if world_map[y][x] == 5:
                spikes.append([x + 0.5, y + 0.5])

            # portal
            if world_map[y][x] == 6:
                p_portal = [x + 0.5, y + 0.5]

    totale_score = len(sprites)

    # ---> Random spawnpunt berekenen voor de ghost <--- #
    k = random.randint(0, 4)
    try:
        p_ghost = possibleSpawns[k]
        or_p_ghost = p_ghost
    except IndexError:
        p_ghost = possibleSpawns[0]
        or_p_ghost = p_ghost

    # ---> SDL2 initialiseren <--- #
    # Initialiseer de SDL2 bibliotheek
    sdl2.ext.init()

    # Maak een venster aan om de game te renderen
    window = sdl2.ext.Window("Project Ingenieursbeleving 2", size=(BREEDTE, HOOGTE))
    window.show()

    # Begin met het uitlezen van input van de muis en vraag om relatieve coordinaten
    sdl2.SDL_SetRelativeMouseMode(True)

    # Maak een renderer aan zodat we in ons venster kunnen renderen
    renderer = sdl2.ext.Renderer(window)
    renderer.blendmode = SDL_BLENDMODE_MOD

    # ---> Textures inladen <--- #
    resources = sdl2.ext.Resources(__file__, "src")
    factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
    texture = factory.from_image(resources.get_path("wall.png"))
    coffin_dance = factory.from_image(resources.get_path("coffin_dance.jpg"))
    controller = factory.from_image(resources.get_path("_MemeController.png"))

    # ---> Sprites inladen <--- #
    sprites_image = [factory.from_image(resources.get_path("full-moon.jpg")),  # Lucht
                     factory.from_image(resources.get_path("emerald.png")),  # Emerald
                     factory.from_image(resources.get_path("world-map.png")),
                     factory.from_image(resources.get_path("ghost.png")),  # Map
                     factory.from_image(resources.get_path("world-map-ended.png")),
                     factory.from_image(resources.get_path("portal.png")),
                     factory.from_image(resources.get_path("jumpscare.jpg")),
                     factory.from_image(resources.get_path("blood.png")),
                     ]

    # ---> Spikes inladen <--- #
    spike_images = [factory.from_image(resources.get_path("1_edit.png")),  # korte spikes
                    factory.from_image(resources.get_path("2_edit.png")),
                    factory.from_image(resources.get_path("3_edit.png")),
                    factory.from_image(resources.get_path("4_edit.png")),
                    factory.from_image(resources.get_path("5_edit.png")),
                    factory.from_image(resources.get_path("6_edit.png")),  # lange spikes
                    ]

    # ---> Fonts initialiseren <--- #
    ManagerFont = sdl2.ext.FontManager(font_path=resources.get_path("opensans.ttf"), size=18)  # Creating Font Manager
    ManagerFontPaused = sdl2.ext.FontManager(font_path=resources.get_path("opensans.ttf"), size=40)
    ManagerFontSelected = sdl2.ext.FontManager(font_path=resources.get_path("opensans.ttf"), size=18, color=kleuren[3])

    text = factory.from_text(f"Score: {str(score)} Lifes: {str(lifes)} FPS: {round(1 / delta, 2)}",
                             fontmanager=ManagerFont)
    textInfo = factory.from_text("Press the red button to pause the game.",
                                 fontmanager=ManagerFont)

    factory.from_text(f"Sprint: {'enabled' if sprint else 'disabled'}",
                             fontmanager=ManagerFont)

    # Functies al eens callen zodat ze al compileren voordat de game start
    bereken_r_straal(np.array([0.79197326, -0.61055577]), 81, np.array([-0.61055577, -0.79197326]), 1)
    raycast(np.array([5.94384612, 16.29289322]), np.array([0.99986466, 0.01645179]), 360, world_map, np.array([0.79197326, -0.61055577]))

    # ---> Main game loop <--- #
    # Blijf frames renderen tot we het signaal krijgen dat we moeten afsluiten
    while not moet_afsluiten:
        start_time = time.time()
        answer = "w!"
        response = arduino.read(arduino.inWaiting()).decode().strip()

        # Onthoud de huidige tijd
        # kolom = 0
        end_game = False
        z_buffer = []

        # Reset de rendering context
        renderer.clear()

        # ---> Begin scherm <--- #
        if begin:
            renderer.draw_rect((0, 0, window.size[0], window.size[1]), kleuren[0])

            textGameInfo = factory.from_text("Try to collect all the gems in the map, once finished find the portal "
                                             "to complete the game.",
                                             fontmanager=ManagerFont)
            renderer.copy(textGameInfo, dstrect=(int(window.size[0] / 2 - textGameInfo.size[0] / 2), 25,
                                                 textGameInfo.size[0], textGameInfo.size[1]))

            textGameInfo = factory.from_text("But watch out! This place is haunted, people claim to have seen ghosts "
                                             "around.",
                                             fontmanager=ManagerFont)
            renderer.copy(textGameInfo, dstrect=(int(window.size[0] / 2 - textGameInfo.size[0] / 2), 65,
                                                 textGameInfo.size[0], textGameInfo.size[1]))

            textGameInfo = factory.from_text("Also, there are traps hidden for intruders, so keep an eye on that!",
                                             fontmanager=ManagerFont)
            renderer.copy(textGameInfo, dstrect=(int(window.size[0] / 2 - textGameInfo.size[0] / 2), 105,
                                                 textGameInfo.size[0], textGameInfo.size[1]))
            renderer.copy(controller, dstrect=(int(window.size[0] / 2 - controller.size[0] / 2), 150,
                                               controller.size[0], controller.size[1]))

            if startCount % 20 == 0:
                font = ManagerFont
            elif startCount % 10 == 0:
                font = ManagerFontSelected

            textGameInfo = factory.from_text("Run forward to start",
                                             fontmanager=font)
            renderer.copy(textGameInfo,
                          dstrect=(int(window.size[0] / 2 - textGameInfo.size[0] / 2), 550,
                                   textGameInfo.size[0], textGameInfo.size[1]))
            startCount += 1

            time.sleep(0.05)  # Frame rate droppen, anders divide by zero error als je uit dit scherm gaat (FPS te hoog)

        # ---> Pauze scherm <--- #
        elif paused:
            renderer.draw_rect((0, 0, window.size[0], window.size[1]), kleuren[0])

            textPaused = factory.from_text("PAUSED",
                                           fontmanager=ManagerFontPaused)
            renderer.copy(textPaused, dstrect=(int(window.size[0] / 2 - textPaused.size[0] / 2), 20,
                                               textPaused.size[0], textPaused.size[1]))

            textSettings1 = factory.from_text("Use the left and right button to edit the settings",
                                              fontmanager=ManagerFont)
            renderer.copy(textSettings1, dstrect=(int(window.size[0] / 2 - textSettings1.size[0] / 2), 100,
                                                  textSettings1.size[0], textSettings1.size[1]))

            textSettings2 = factory.from_text("and use the backwords button to switch to a different setting!",
                                              fontmanager=ManagerFont)
            renderer.copy(textSettings2, dstrect=(int(window.size[0] / 2 - textSettings2.size[0] / 2), 120,
                                                  textSettings2.size[0], textSettings2.size[1]))

            textFOV = factory.from_text(f"Field of view (FOV): {FOV}",
                                        fontmanager=ManagerFont if tab % 2 == 1 else ManagerFontSelected)
            renderer.copy(textFOV, dstrect=(int(window.size[0] / 2 - textFOV.size[0] / 2), 160,
                                            textFOV.size[0], textFOV.size[1]))

            textSensitivity = factory.from_text(f"Sensitivity: {sensitivity}",
                                                fontmanager=ManagerFont if tab % 2 == 0 else ManagerFontSelected)
            renderer.copy(textSensitivity, dstrect=(int(window.size[0] / 2 - textSensitivity.size[0] / 2), 200,
                                                    textSensitivity.size[0], textSensitivity.size[1]))

            textClose = factory.from_text("Run forward to resume.",
                                          fontmanager=ManagerFont)
            renderer.copy(textClose, dstrect=(int(window.size[0] / 2 - textClose.size[0] / 2), 240,
                                              textClose.size[0], textClose.size[1]))

            d_camera = math.atan(math.radians(FOV))
            time.sleep(0.05)  # Frame rate droppen

        # ---> Win scherm <--- #
        elif won:
            renderer.draw_rect((0, 0, window.size[0], window.size[1]), kleuren[0])

            textPaused = factory.from_text("You Win!",
                                           fontmanager=ManagerFontPaused)
            renderer.copy(textPaused, dstrect=(int(window.size[0] / 2 - textPaused.size[0] / 2), 20,
                                               textPaused.size[0], textPaused.size[1]))

            textSettings1 = factory.from_text("Press ESC to quit",
                                              fontmanager=ManagerFont)
            renderer.copy(textSettings1, dstrect=(int(window.size[0] / 2 - textSettings1.size[0] / 2), 500,
                                                  textSettings1.size[0], textSettings1.size[1]))

            time.sleep(0.05)  # Frame rate droppen

        # ---> Game over scherm <--- #
        elif gameOver:
            renderer.draw_rect((0, 0, window.size[0], window.size[1]), kleuren[0])
            renderer.copy(coffin_dance,
                          (0, 0, coffin_dance.size[0], coffin_dance.size[1]),
                          (75, 100, int(coffin_dance.size[0] / 2), int(coffin_dance.size[1] / 2)))

            textPaused = factory.from_text("Game Over!",
                                           fontmanager=ManagerFontPaused)
            renderer.copy(textPaused, dstrect=(int(window.size[0] / 2 - textPaused.size[0] / 2), 20,
                                               textPaused.size[0], textPaused.size[1]))

            textSettings1 = factory.from_text("Press ESC to quit.",
                                              fontmanager=ManagerFont)
            renderer.copy(textSettings1, dstrect=(int(window.size[0] / 2 - textSettings1.size[0] / 2), 500,
                                                  textSettings1.size[0], textSettings1.size[1]))

            time.sleep(0.05)  # Frame rate droppen

        # ---> jumpscare scherm <--- #
        elif jumpscare:
            renderer.copy(sprites_image[6], srcrect=(0, 0, sprites_image[6].size[0], sprites_image[6].size[1]),
                          dstrect=(0, 0, window.size[0], window.size[1]))

            jumpscareCount += 1
            time.sleep(1 / jumpscareLength)

            if jumpscareCount >= jumpscareLength:
                jumpscare = False
                jumpscareCount = 0

        # ---> Main game loop <--- #
        else:
            # ---> Deur openen als alle gems weg zijn <--- #
            distanceToGhost = math.sqrt(pow(p_ghost[0] - p_speler[0], 2) + pow(p_ghost[1] - p_speler[1], 2))
            if distanceToGhost <= 5:
                answer += "ocnef"
            elif distanceToGhost <= 10:
                answer += "ocnel"
            elif distanceToGhost <= 15:
                answer += "ocnkl"
            elif distanceToGhost <= 20:
                answer += "ocjkl"
            else:
                answer += "aijkl"

            if score == totale_score:
                world_map[p_deur[1]][p_deur[0]] = 0
                end_game = True

            # ---> Vertical raycast <--- #
            for kolom in range(1, window.size[0]):
                r_straal = bereken_r_straal(r_speler, kolom, r_cameravlak, d_camera)
                (d_muur, textuur_x) = raycast(p_speler, r_straal, texture.size[0], world_map, r_speler)
                render_kolom(texture, sprites_image, renderer, window, kolom, d_muur, textuur_x)
                z_buffer.append(d_muur)

            # ---> Sprites <--- #
            for sprite in sprites:
                if np.array_equal(p_speler.astype(int), [int(sprite[0]), int(sprite[1])]):
                    score += 1

                    if len(str(score)) < 2:
                        score = '0' + str(score)
                    answer += f"({score})"
                    score = int(score)

                    sprites.remove(sprite)
                    Mix_PlayChannel(-1, gemPickup, 0)
                else:
                    render_sprite(sprites_image[1], sprite, p_speler, renderer, window, z_buffer)

            # ---> Ghost <--- #
            p_ghost, possibleDirections, ghostDirection, moveCounter = \
                ghost_movement(p_ghost, possibleDirections, ghostDirection, moveCounter, delta)

            # Int nemen van elke coëfficient in de array -> makkelijker checken ofdat de gem gecollect is
            if np.array_equal(p_speler.astype(int), [int(p_ghost[0]), int(p_ghost[1])]):
                lifes -= 1
                jumpscare = True
                blood = True
                sensitivity = sensitivity // 50
                Mix_PlayChannel(-1, scream, 0)
                answer += 'b'
                answer += 'v'

                k = random.randint(0, 4)
                try:
                    p_ghost = possibleSpawns[k]
                except IndexError:
                    p_ghost = possibleSpawns[0]

            render_sprite(sprites_image[3], p_ghost, p_speler, renderer, window, z_buffer)

            # ---> Spikes / Traps <--- #
            for spike in spikes:
                # Spikes aanzetten
                if not spikes_animation and (np.array_equal(p_speler.astype(int), [int(spike[0]), int(spike[1])])
                                             or np.array_equal(p_speler.astype(int), [int(spike[0] + 1), int(spike[1])])
                                             or np.array_equal(p_speler.astype(int), [int(spike[0] - 1), int(spike[1])])
                                             or np.array_equal(p_speler.astype(int), [int(spike[0]), int(spike[1] + 1)])
                                             or np.array_equal(p_speler.astype(int),
                                                               [int(spike[0]), int(spike[1] - 1)])):
                    spikes_animation = True
                    Mix_PlayChannel(-1, spike_sound, 0)

                if spikes_animation:
                    if spikes_count >= 2.24:
                        spikes_animation = False
                        spikes_count = -2.24
                    else:
                        spikes_count += delta / 5

                    if np.array_equal(p_speler.astype(int), [int(spike[0]), int(spike[1])]):
                        lifes -= 1
                        Mix_PlayChannel(-1, oof, 0)
                        blood = True
                        sensitivity = sensitivity // 50
                        spikes.remove(spike)
                        answer += "v"
                    else:
                        y = -pow(spikes_count, 2) + 5
                        render_sprite(spike_images[round(y)], spike, p_speler, renderer, window, z_buffer, spike)

            # ---> Portal in het midden <--- #
            render_sprite(sprites_image[5], p_portal, p_speler, renderer, window, z_buffer)

            # ---> Minimap / Text <--- #
            text = factory.from_text(f"Score: {score}/{totale_score} Lifes: {str(lifes)}\nFPS: {round(1 / delta, 2)}",
                                     fontmanager=ManagerFont)
            sprint_text = factory.from_text(f"Sprint: {'enabled' if sprint else 'disabled'}",
                                            fontmanager=ManagerFont)
            render_static(renderer, p_speler, sprites_image[2] if not end_game else sprites_image[4], sprites, text,
                          textInfo, sprint_text, window)

            # ---> Bloed als leven kwijt <--- #
            if blood:
                renderer.copy(sprites_image[7], srcrect=(0, 0, sprites_image[7].size[0], sprites_image[7].size[1]),
                              dstrect=(0, 0, window.size[0], window.size[1]))
                bloodCount += 1
                if bloodCount >= bloodLength:
                    blood = False
                    bloodCount = 0
                    sensitivity = int(sensitivity * 50)

            # ---> Game over <--- #
            if lifes == 0:
                gameOver = True
                answer += "g"

            # ---> Gewonnen <--- #
            if np.array_equal(p_speler.astype(int), [int(p_portal[0]), int(p_portal[1])]):
                won = True

        # ---> Verwissel de rendering context met de frame buffer <--- #
        renderer.present()
        end_time = time.time()
        delta = end_time - start_time
        verwerk_input(delta)
        # print("Answer: " + answer)
        # print("Response: " + response)
        arduino.write(answer.encode())
        window.refresh()

    # ---> SDL2 afsluiten <--- #
    Mix_CloseAudio()
    SDL_Quit(SDL_INIT_AUDIO)
    sdl2.ext.quit()


if __name__ == '__main__':
    main()
