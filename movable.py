#!/usr/bin/python
# -*- coding: utf-8 -*-
#zápočotvý program NPRG031
#rok 2012/2013, letní semestr
#autor: Vojtěch Hudeček

#soubor movable.py
#import balíčků
import pygame
import random
import math
from config import *

class ImageStorage():
    """
    pomocná třída pouze pro uchování seznamu obrázků pohybujících se objektů
    vytvoří seznam seznamů - pro každý směr libovolně dlouhý seznam měnícíh se obrázků
    """
    def __init__(self,up,right,down,left):
        self.images = list()
        self.images.append(list())
        for im in up:
            self.images[0].append(pygame.image.load('./images/'+im).convert())
        self.images.append(list())
        for im in right:
            self.images[1].append(pygame.image.load('./images/'+im).convert())
        self.images.append(list())
        for im in down:
            self.images[2].append(pygame.image.load('./images/'+im).convert())
        self.images.append(list())
        for im in left:
            self.images[3].append(pygame.image.load('./images/'+im).convert())

class Movable(pygame.sprite.Sprite):
    """
    rodičovská třída všech pohybujících se objektů
    dědí od třídy pygame.sprite.Sprite, což umožňuje detekci kolizí
    """
    def __init__(self,direction,direction_no,images,delta,name,position,game,x,y,speed):
        pygame.sprite.Sprite.__init__(self)
        #počet pixelů posunutí za tah
        self.speed = speed
        #statistiky
        self.monsters_killed = 0
        self.players_killed = 0
        #jí tabletky?
        self.eating = True
        #je v procesu změny směru?
        self.changing = False
        #barva kruhu
        self.color = red
        #počet tahů boss režimu
        self.boss = 0
        #má kruh?
        self.ring = False
        #pohybuje se?
        self.moving = False
        #následující směr
        self.new_direction = [0,0]
        #číslo směru
        self.new_dir_no = 0
        #počet kroků - počítaní pro účely změny obraázku
        self.steps = 0
        #celkový počet kroků
        self.steps_total = 0
        #souřadnice vzhledem k herním pozicím
        self.x = x
        self.y = y
        #souřadnice poslední změny směru
        self.last_xy = [0,0]
        #opakující se změny směru na malém místě
        self.repeats = 0
        #změny souřadnic pro účely výpočtu herních souřadnic
        self.change_x = 0
        self.change_y = 0
        #index aktuálního obrázku
        self.current_step = 0
        # stoupání nebo klesání indexu aktuálního obrázku
        self.change = 1
        #číslo směru
        self.direction_no = direction_no
        #vektor směru
        self.direction = direction
        #instance třídy Game
        self.game = game
        #instance ImageStorage
        self.images = images
        #aktuální obrázek, souřadnice - pro účely vykreslení přes skupinu  movable_list
        self.image = self.images.images[0][0]
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        #udává počet tahů na změnu obrázku
        self.delta = delta
        #jméno
        self.name = name
        #skutečné souřadnice
        self.position = position
        #skóre
        self.score = 0
        #inicializace zvuků
        pygame.mixer.init()
        self.beep = pygame.mixer.Sound('./sounds/pickup.wav')
        self.beep.set_volume(0.3)
        self.boost = pygame.mixer.Sound('./sounds/boost.wav')
        self.boost.set_volume(0.5)
        self.hurt = pygame.mixer.Sound('./sounds/hurt.wav')
        self.hurt.set_volume(0.3)

    def isAbleToMove(self):
        """
        funkce vrátí boolean hodnotu, je-li v aktuílním směru možné pokračovat
        """
        if(self.y >= self.game.maze.height) or (self.x >= self.game.maze.width)  or (self.x < 0) or (self.y < 0):
            return False
        if self.game.maze.maze_map[self.y + (self.direction[1])][self.x + (self.direction[0])] != '*':

            return True
        else:
            return False

    def changeDirection(self,new_direction,new_dir_no):
        """
        změní směr pohybu (pokusí se)
        """
        if self.eating:
            #uložení směru do "paměti"
            self.next_direction = [new_direction,new_dir_no]
        #nastavení nového směru
        self.new_direction = new_direction
        self.new_dir_no = new_dir_no
        #příznak změny směru
        self.changing = True
        if not self.moving:
            #stojí, změna se zavolá hned
            self.makeChange()
        #jinak se změna zavolá po dosažení nové herní souřadnice

    def makeChange(self):
        """
        provede změnu směru, je-li to možné
        """
        #zapamatování starého směru
        old_direction = self.direction
        old_no = self.direction_no
        #nastavení nového
        self.direction = self.new_direction
        self.direction_no = self.new_dir_no
        #může se hýbat?
        if self.isAbleToMove():
            #ano, změna hotova, reset paměti
            self.changing = False
            if self.eating:
                self.next_direction = list()
            return
        else:
            #nemůže se hýbat, změna neúspěšná, nastavení původního směru
            self.changing = False
            self.direction = old_direction
            self.direction_no = old_no
            return

    def compute_distance(self,xy):
        """
        spočítá vzdálenost z dalšího pole ve směru k cíli
        """
        dist = math.sqrt(math.pow(abs(self.x + self.direction[0] - xy[0]),2) + math.pow(abs(self.y + self.direction[1] - xy[1]),2))
        return int(dist)

    def changePosition(self):
        """
        volá se po dosažení nových herních souřadnic
        provede aktualizaci stavu, pozice a v případě monstra rozhodne o dalším postupu
        """
        if not self.eating:
        #monstrum si počítá kroky
            self.steps_total += 1
        directions = [[[0,-1],0],[[1,0],1],[[0,1],2],[[-1,0],3]]
        if abs(self.direction[0]) == 1:
            #pohyb v x-ové ose, zkouší změnu v y
            try_directions = [[[0,-1],0],[[0,1],2]]
        else:
            #pohyb v y-ové ose, zkouší změnu v x
            try_directions = [[[-1,0],3],[[1,0],1]]
        prop = random.randrange(0,101)
        #podle pravděpodobnosti se rozhodne, jestli se zachová nejlíp jak může nebo náhodně
        #prvních 40 kroků se tak zachová vždy
        if ((prop <= self.hunt) or self.steps_total <= 40) and (len(self.game.pac_list) > 0) :
            for i in range(2):
                #zkouší směry
                if (self.game.maze.maze_map[self.y + try_directions[i][0][1]][self.x + try_directions[i][0][0]] != '*'):
                    #detekována křižovatka
                    if not self.eating:
                        #je-li křižovatka v blízkosti minulé změny, zvýší počet opakování
                        if (self.compute_distance(self.last_xy) < 10):
                            self.repeats += 1
                        else:
                        #nastaví nové místo změny směru
                            self.last_xy = [self.x,self.y]
                            self.repeats = 0
                        self.moving = False
                        min = 1000
                        max = 0
                        if (not self.game.pac_list.__contains__(self.target)) and (len(self.game.pac_list) > 0):
                        #má-li smysl vybírat cestu k cíli
                            self.target = self.game.pac_list[random.randrange(len(self.game.pac_list))]
                        if self.repeats < 7:
                            #neopakuje se dlouho
                            #podle toho zda pronásleduje nebo nadbíhá zvolí cílovou pozici
                            if not self.chaser:
                                delta_x = self.target.direction[0]*10
                                delta_y = self.target.direction[1]*10
                            else:
                                delta_x = 0
                                delta_y = 0
                            dir = random.randrange(4)
                            for i in range(4):
                                #vybere nejlepší směr (nejblíž cíli, pokud není boss, jinak nejdál)
                                self.changeDirection(directions[i][0],directions[i][1])
                                if self.direction == directions[i][0]:
                                    dist = self.compute_distance([self.target.x + delta_x,self.target.y + delta_y])
                                    if self.target.boss == 0:
                                        if (dist <= min):
                                                min = dist
                                                dir = i
                                    else:
                                       if (dist > max):
                                            max = dist
                                            dir = i
                            #změní směr
                            self.changeDirection(directions[dir][0],directions[dir][1])
                        else:#opakuje se často - náhodný výběr
                            self.moving = False
                            r = random.randrange(2)
                            self.changeDirection(try_directions[r][0],try_directions[r][1])
                    else:
                        #pokud má pacman v paměti změnu směru, změní ho
                        if len(self.next_direction) > 0:
                            self.changeDirection(self.next_direction[0],self.next_direction[1])

                    break
        if self.eating:
            #připočtení či odečtení bodů
            if self.game.maze.maze_map[self.y][self.x] == '_':
                self.score += 1
                self.game.maze.feeds -= 1
                self.beep.play()
                self.game.maze.maze_map[self.y][self.x] = '0'
            if self.game.maze.maze_map[self.y][self.x] == '-':
                self.score -= 1
                self.hurt.play()

            if self.game.maze.maze_map[self.y][self.x] == '/':
                self.color = cyan
                self.boost.play()
                self.ring = True
                self.speed = speed_pac + 1
                self.boss = 500
                self.game.maze.maze_map[self.y][self.x] = '0'
        else:
            #pokud se monstrum nemůže pohnout, to znamená opakuje se a narazilo, zvolí náhodně
            self.moving = False
            while not self.isAbleToMove():
                r = random.randrange(4)
                self.changeDirection(directions[r][0],directions[r][1])
        #změna pozice při vstupu do teleportu
        if (ord(self.game.maze.maze_map[self.y][self.x]) >= 49) and (ord(self.game.maze.maze_map[self.y][self.x]) <= 57):
            value = self.game.maze.ports[int(self.game.maze.maze_map[self.y][self.x])][0]
            if (value[0] == self.y) and (value[1] == self.x):
                new = self.game.maze.ports[int(self.game.maze.maze_map[self.y][self.x])][1]
            else:
                new = self.game.maze.ports[int(self.game.maze.maze_map[self.y][self.x])][0]
            self.position = self.game.compute_position(new)
            self.x = new[1]
            self.y = new[0]
            self.moving = False
            #korekce směru, aby nestál v bráně
            if not self.isAbleToMove():
                self.changeDirection([0,-1],0)
            if not self.isAbleToMove():
                self.changeDirection([1,0],1)
            if not self.isAbleToMove():
                self.changeDirection([0,1],2)
            if not self.isAbleToMove():
                self.changeDirection([-1,0],3)
            self.moving = False

    def moveIt(self,screen):
        """
        provede posunutí objektu o vektor rychlosti
        """
        if True:
            #odečtení času, případně vrácení původní rychlosti
            if self.boss > 0:
                self.boss -= 1
            else:
                self.speed = speed_pac
                if(self.color == cyan):
                    self.ring = False
            self.moving = False
            #posunutí, aktualizace celkové změny
            if (self.isAbleToMove()) and (self.direction != [0,0]):
                self.moving = True
                self.position[0] += self.direction[0] * self.speed
                self.position[1] += self.direction[1] * self.speed
                self.change_x += self.direction[0] * self.speed
                self.change_y += self.direction[1] * self.speed
            #v případě přechodu na další čtverec úprava souřadnic
            if (self.change_x >= 10):
                self.change_x -= 10
                self.x += 1
                self.changePosition()
                if self.changing:
                    self.makeChange()
            if (self.change_x <= -10):
                self.change_x += 10
                self.x -= 1
                self.changePosition()
                if self.changing:
                    self.makeChange()
            if (self.change_y >= 10):
                self.change_y -= 10
                self.y += 1
                self.changePosition()
                if self.changing:
                    self.makeChange()
            if (self.change_y <= -10):
                self.change_y += 10
                self.y -= 1
                self.changePosition()
                if self.changing:
                    self.makeChange()
            #úprava souřadnic pro vykreslení
            self.rect.x= self.position[0]
            self.rect.y= self.position[1]
            self.image = self.images.images[self.direction_no][self.current_step]
            self.image.set_colorkey(black)
            #vykreslení kruhu, je-li třeba
            if self.ring:
                ellipse = pygame.Surface((22,22))
                ellipse.fill(black)
                pygame.draw.ellipse(ellipse,self.color,[0,0,22,22],7)
                ellipse.set_alpha(180)
                ellipse.set_colorkey(black)
                screen.blit(ellipse,[self.position[0]-3,self.position[1]-3])
            self.steps += 1
            #případná změna obrázku
            if self.steps >= self.delta:
                self.steps = 0
                self.current_step += self.change
                if(self.current_step == len(self.images.images[0]) - 1) or (self.current_step == 0):
                    self.change *= -1

    def die(self,list):
        """"
        odstranění monster zaměřených na tohoto hráče
        """
        for m in list:
            if not m.eating:
                if m.target == self:
                    list.remove(m)

class Pac(Movable):
    """
    třída odvozená od třídy Movable, nastavení pouze některých proměnných
    """
    def __init__(self,direction,direction_no,images,delta,name,position,game,x,y,speed):
        Movable.__init__(self,direction,direction_no,images,delta,name,position,game,x,y,speed)
        self.player = True
        self.hunt = 0
        self.next_direction = list()

    def move(self,screen):
        self.moveIt(screen)

class Monster(Movable):
    """
    třída odvozená od třídy Movable, nastavení pouze některých proměnných
    """
    def __init__(self,direction,direction_no,images,delta,name,position,game,x,y,speed,hunt_q,target,chaser):
        Movable.__init__(self,direction,direction_no,images,delta,name,position,game,x,y,speed)
        self.eating = False
        self.player = False
        self.hunt = hunt_q * 100
        self.target = target
        self.chaser = chaser

    def move(self,screen):
        self.moveIt(screen)

