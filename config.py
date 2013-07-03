#!/usr/bin/python
# -*- coding: utf-8 -*-
#zápočotvý program NPRG031
#rok 2012/2013, letní semestr
#autor: Vojtěch Hudeček

#soubor config.py
#obsahuje nastavení použitých hodnot
#definice barev,rychlosti objektů, jméno fontu

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
blue = (0,0,255)
green = (0,255,0)
pale = (255,255,150)
orange = (255,150,0)
bright_red = (255,0,51)
bright_green = (75,150,26)
yellow = (255,255,0)
cyan = (100,100,255)
purple = (255,0,255)
speed_pac = 2
delta_pac = 4
speed_monster = 4
delta_monster = 4
import os
maze_count = 0
for filename in os.listdir('maps'):
    if filename[:4] == 'map_':
        maze_count += 1
font_name = 'purisa'