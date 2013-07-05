#!/usr/bin/python
# -*- coding: utf-8 -*-
#zápočotvý program NPRG031
#rok 2012/2013, letní semestr
#autor: Vojtěch Hudeček
# coding=utf-8

#soubor game.py obsahuje definice tříd Maze, Menu, Game

#import balíčků
import pygame
from config import *
from movable import *

class Maze():
    """
    Třída Maze obsahuje matici reprezentující hrací plochu a další informace o ní

    """
    def __init__(self,width,height,mazeNo):
        #výška a šířka pole
        self.width = width
        self.height = height
        #matice obsahující jednotlivé pozice
        self.maze_map = [[0 for x in range(width)] for x in range(height)]
        #seznam teleportů, obsahuje vždy dvě hodnoty, což jsou souřadnice obou konců
        self.ports = [[[0,0] for x in range(2)] for x in range(10)]
        #seznam pozic monster
        self.positions = list()
        self.pac_positions = list()
        #počet tabletek k jídlu
        self.feeds = 0
        #inicializace bludiště
        self.initMaze(mazeNo)

    def initMaze(self,mazeNo):
       """

       inicializuje bludiště pomocí čísla mapy z příslušného souboru

       """
       try:
           maze_file = open('./maps/map_'+str(mazeNo)+'.txt','r')
           #vynechá všechny řádky až do @
           while maze_file.readline().strip() != '@':
               continue
            #čte soubor a ukládá hodnoty do matice
           for i in range(len(self.maze_map)):
               for j in range(len(self.maze_map[i])):
                   self.maze_map[i][j] = maze_file.read(1)
                   #jeden z konců teleportu
                   if (ord(self.maze_map[i][j]) >= 49) and (ord(self.maze_map[i][j]) <= 57):
                       #indexováno čísly 1-9
                       index = int(self.maze_map[i][j])
                       value = self.ports[index][0]
                       #první nebo druhý vstup
                       if value == [0,0]:
                           self.ports[index][0] = [i,j]
                       else:
                           self.ports[index][1] = [i,j]
                    #pozice pro monstra
                   if(self.maze_map[i][j] == '^'):
                        self.positions.append([i,j])
                   if(self.maze_map[i][j] == 'P'):
                        self.pac_positions.append([i,j])
                    #pozice s tabletkou
                   if self.maze_map[i][j] == '_':
                        self.feeds += 1
               maze_file.readline()
           maze_file.close()
       except Exception as e:
           print e
           print 'Error opening file "map_' + str(mazeNo) + '"'


class Menu:
    """
    třída pro zobrazení a ovládání menu
    """
    def __init__(self,list):
        """
        seznam položek menu
        """
        self.list = list
        self.active = 0

    def up(self):
        """
        posunutí nahoru
        """
        if self.active -1 >= 0:
            self.active -= 1

    def down(self):
        """
        posunutí dolů
        """
        if self.active +1 < len(self.list):
            self.active += 1

    def getName(self,screen,name):
        """
        spustí vlastní cyklus, zabrání hlavnímu cylku reagovat na události
        poskytuje možnost jednoduché editace daného jména,
        po stisknutí klávesy Enter vrátí výsledek
        """
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        if len(name) > 0:
                            name = name[:-1]
                    else:
                        try:
                            name += chr(event.key)
                        except:
                            print 'Only lowercase, please'
            rect = pygame.Surface((200,50))
            rect.fill(black)
            label_font = pygame.font.SysFont(font_name, 20)
            label = label_font.render(name+'|', 1, pale)
            rect.blit(label,(25,10))
            screen.blit(rect,(950,150))
            pygame.display.flip()
        return name

    def doAction(self,game):
        """
        vrátí aktivní položku
        """
        action = self.list[self.active]
        return action


    def show(self,screen,names,count):
        """
        vykreslení menu pomocí seznamu
        """
        rect = pygame.Surface((201,251))
        rect.fill(black)
        label_font = pygame.font.SysFont(font_name, 20)
        for i in range(len(self.list)):
            if self.active == i:
                label = label_font.render(self.list[i], 1, pale)
            else:
                label = label_font.render(self.list[i], 1, red)
            rect.blit(label,(25,10 + i*35))
        pygame.draw.rect(rect,blue,[0,0,200,250],2)
        shadow = pygame.Surface((1350,730))
        shadow.fill(black)
        shadow.set_alpha(200)
        screen.blit(shadow,(0,0))
        screen.blit(rect,(950,200))

class Game():
    """
    třída Game nese informace o aktuálním stavu hry
    umožňuje vykreslení hrací plochy a menu, používá tříd Menu a Maze
    """
    def __init__(self):
        #výchozí číslo bludiště
        self.maze_no = 1
        #barvy teleporů
        self.colors = list()
        self.color_count = 0
        #seznam AKTIVNÍCH hráčů
        self.pac_list = list()
        #seznam jmen hráčů
        self.static_list = ['','','','']
        #seznam monster
        self.monster_list = list()
        #vytvoření menu
        self.menu = Menu(['Return','New game','Choose a map','Add player','Remove player','Rename players','Quit'])
        #řídící proměnná hlavního cyklu
        self.done = False
        #jméno písně
        self.song_name = 'zion.mp3'
        #výchozí počet monster na každého hráče
        self.monsters_per_player = 3

    def sort(self,list):
        """
        funkce seřadí pomocí bubble sortu list objektů typu movable
        podle skóre
        """
        for p in range(len(list)-1):
                for i in range(len(list)-1):
                    if list[i].score < list[i+1].score:
                        x = list[i]
                        list[i] = list[i+1]
                        list[i+1] = x

    def move(self,screen):
        """
        provedení tahu
        všechny pohybující se objekty provedou tah a poté je vyhodnocen nový stav hry
        prvním třem hráčům se vykreslí barevný kruh, pokud nejsou v režimu boss
        """
        for pac in self.pac_list:
            pac.move(screen)
        for monster in self.monster_list:
            monster.move(screen)
        if len(self.pac_list) > 1:
            self.sort(self.pac_list)
            for p in self.pac_list:
                if p.boss == 0:
                    p.ring = False
            self.pac_list[0].ring = True
            if self.pac_list[0].boss == 0:
                self.pac_list[0].color = bright_red
            self.pac_list[1].ring =  True
            if self.pac_list[1].boss == 0:
                self.pac_list[1].color = purple
            if (len(self.pac_list) > 2) and (self.pac_list[2].boss == 0):
                self.pac_list[2].ring = True
                self.pac_list[2].color = bright_green
        elif (len(self.pac_list) == 1) and (self.pac_list[0].boss == 0):
            self.pac_list[0].ring = False

    def setMazeNo(self,no):
        """
        procedura nastaví jiné bludiště
        přečte ifnormace z daného souboru a vytvoří novou instanci třídy Maze
        """
        self.maze_no = no
        maze_file = open('./maps/map_'+str(no)+'.txt','r')
        #šířka a výška, jméno písně
        width = int(maze_file.readline())
        height = int(maze_file.readline())
        name = maze_file.readline().strip()
        self.song_name = name
        line = maze_file.readline().strip()
        i = 0
        #načtení barev teleportů
        while line != '@' :
               eval('self.colors.append(' + line + ')')
               i +=1
               self.color_count += 1
               line = maze_file.readline().strip()
        #vytvoření nové instance třídy Maze
        self.maze = Maze(width,height,no)

    def showMenu(self,screen,count,names):
        """
        zobrazí menu
        """
        self.menu.show(screen,count,names)

    def draw(self,screen,count):
        """
        Vykreslí bludiště pomocí objektu třídy Maze
        dále vykreslí zbylé části okna
        """
        #souřadnice levého horního rohu bludiště
        y=57
        x=135
        #prochází bludiště
        for i in range(len(self.maze.maze_map)):
            for j in range(len(self.maze.maze_map[i])):
                #dvě * pod sebou nebo vedle sebe spojí čárou
                if (j < len(self.maze.maze_map[i])-1) and (self.maze.maze_map[i][j] == '*') and (self.maze.maze_map[i][j+1] == '*'):
                    pygame.draw.line(screen,self.colors[0],(x+4,y+3),(x+15,y+3),2)
                if (i < len(self.maze.maze_map)-1) and (self.maze.maze_map[i][j] == '*') and (self.maze.maze_map[i+1][j] == '*'):
                    pygame.draw.line(screen,self.colors[0],(x+4,y+4),(x+4,y+14),2)
                #vykreslení teleportů
                elif (ord(self.maze.maze_map[i][j]) >= 49) and (ord(self.maze.maze_map[i][j]) <= 57):
                    pygame.draw.ellipse(screen,self.colors[int(self.maze.maze_map[i][j])],[x,y-6,10,18],1)
                #vykreslení tabletek
                elif self.maze.maze_map[i][j] == '_':
                    pygame.draw.circle(screen,pale,[x+5,y+5],1,1)
                #pole ubírající body
                elif self.maze.maze_map[i][j] == '-':
                    pygame.draw.circle(screen,red,[x+5,y+5],2,1)
                #tableta přecházející do režimu boss
                elif self.maze.maze_map[i][j] == '/':
                    pygame.draw.circle(screen,yellow,[x+5,y+5],4,3)
                x+= 10
            y += 10
            x = 135
        #podle počtů hráčů vykreslí ovládání a jména hráčů v daných rozích
        label_font = pygame.font.SysFont(font_name, 20)
        score_font = pygame.font.SysFont("monospace", 20)
        wasd = pygame.image.load('./images/wasd.png').convert()
        ijkl = pygame.image.load('./images/ijkl.png').convert()
        arrows = pygame.image.load('./images/arrows.png').convert()
        num = pygame.image.load('./images/8456.png').convert()
        if count > 0:
            label = label_font.render(self.static_list[0], 1, yellow)
            screen.blit(label, (5,140))
            screen.blit(arrows,(5,70))
        if count > 1:
            label = label_font.render(self.static_list[1], 1, yellow)
            screen.blit(label, (950,140))
            screen.blit(wasd,(950,70))
        if count > 2:
            label = label_font.render(self.static_list[2], 1, yellow)
            screen.blit(label, (5,640))
            screen.blit(ijkl,(5,570))
        if count > 3:
            label = label_font.render(self.static_list[3], 1, yellow)
            screen.blit(label, (950,640))
            screen.blit(num,(950,570))
        #horní lišta s klávesovými zkratkami
        label = score_font.render('Restart F5   Music F6   Pause F9   Menu F10   Fulscreen F11   Quit F12', 1, red)
        screen.blit(label, (5,10))
        label = score_font.render('Monsters per player(+/-): '+str(self.monsters_per_player), 1, red)
        screen.blit(label, (900,10))
        y_delta = 0
        i = 0
        #vykreslení stavu hry v pravé části okna - jména hráčů a dosažená skóre
        #hráči jsou vypsáni barvou, podle pořadí
        #v režimu boss je jejich jméno modré a je vidět zbývající čas
        for pac in self.pac_list:
            col = yellow
            label = pac.name
            if i == 0:
                col = bright_red
            elif i == 1:
                col = purple
            elif i == 2:
                col = bright_green
            if pac.boss > 0:
                col = blue
                label += ' ' + str(pac.boss)
            label = label_font.render(label, 1, col)
            screen.blit(label, (1180, 100 + y_delta))
            score = score_font.render(str(pac.score),1,(255,180,0))
            screen.blit(score, (1180, 130 + y_delta))
            y_delta += 80
            i += 1

    def compute_position(self,pos):
        """
        spočítá souřadnice v okně ze souřadnic konkrětního pole hracího plánu
        """
        x = 10 * pos[1] + 132
        y = 10 * pos[0] + 52
        return [x,y]