#!/usr/bin/python
# -*- coding: utf-8 -*-
#zápočotvý program NPRG031
#rok 2012/2013, letní semestr
#autor: Vojtěch Hudeček

#soubor Pacmen.py je hlavním souborem programu
#obsahuje hlavní cyklus programu, inicializaci objektů a obsluhu událostí

#importy balíčků
import pygame
from config import *
from game import *
from movable import *
from pygame.locals import *

def showText(screen):
    """
    pomocná procedura, v případě skončení hry je nastavena proměnná show_menu
    a procedura vypíše informace o proběhnuté hře
    """
    game.sort(result_list)
    label_font = pygame.font.SysFont(font_name, 110,True)
    label = label_font.render('Game over',1,(200,0,0))
    if show_menu:
        screen.blit(label,(160,150))
    score_font = pygame.font.SysFont('monospace', 20)
    y_delta = 0
    for pac in result_list:
        pac_score = score_font.render(pac.name + ': ' + str(pac.score),1,yellow)
        pac_monst = score_font.render('Monsters killed: ' + str(pac.monsters_killed),1,yellow)
        pac_play = score_font.render('Players killed: ' + str(pac.players_killed),1,yellow)
        screen.blit(pac_score,(200,320 + y_delta))
        screen.blit(pac_monst,(380,320 + y_delta))
        screen.blit(pac_play,(630,320 + y_delta))
        y_delta += 30

def drawLabels(screen):
    """
    proměnnná labels obsahuje seznam informací určených pro tisk na určité místo obrazovky
    procedura je vytiskne, hlídá také čas zobrazení
    """
    for l in labels:
        if l[2] > 0:
            l[2] -= 1
            font = pygame.font.SysFont('monospace', 17,True)
            lbl = font.render(l[0],1,cyan)
            screen.blit(lbl,l[1])
        else:
            labels.remove(l)

def playDeath(screen,pos,i,j):
    """
    pomocná procedura, po zabití jednoho z hráčů dočasně pozastaví hru a přehraje sérii obrázků
    """
    death_pics = ['d1.png','d2.png','d3.png','d4.png','d5.png','d6.png','d7.png','d8.png']
    img = pygame.image.load('./images/'+death_pics[j]).convert()
    img.set_colorkey(black)
    screen.blit(img,pos)
    pygame.display.flip()
    screen.fill(black)
    if i == 80: #je nutné provést ještě jeden tah, pro odstranění hráče
        game.move(screen)
    game.draw(screen,player_count)
    movable_list.draw(screen)
    i -= 1
    clock.tick(40)
    if i > 0:
        if i % 10 == 0:
            j += 1
        playDeath(screen,pos,i,j)

def movie():
    """
     "okrasná procedura" při zapnutí hry přehraje krátkou scénku, použije vlastní okno
     je možné ji přerušit stiskem kterékoli klávesy
    """
    import os
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (300,190)
    beep = pygame.mixer.Sound('./sounds/pickup.wav')
    beep.set_volume(0.4)
    screen = pygame.display.set_mode([700,350],pygame.NOFRAME)
    label_font = pygame.font.SysFont(font_name, 150,True)
    skip_font = pygame.font.SysFont('monospace', 20)
    skip = skip_font.render('Press any key to skip',1,red)
    pac = pygame.image.load('./images/big_pac_down_open.png').convert()
    pac_up =  pygame.image.load('./images/big_pac_up_open.png').convert()
    pac.set_colorkey(black)
    pac_up.set_colorkey(black)
    label_s = ['P','a','c','m','a','n','']
    i = 0
    clock = pygame.time.Clock()
    while i < 370:
        for event in pygame.event.get():
        #zavření okna
            if event.type == pygame.QUIT:
                i = 400
            if event.type == KEYDOWN:
                i = 400
        screen.fill(black)
        i += 1
        if ((i > 77) and (i < 125)) or ((i > 230) and (i < 280)):
            if i % 4 == 0:
                beep.play()
        if i == 105:
            label_s[4] = '?'
        if i == 275:
            label_s[4] = 'e'
            label_s[6] = '!'
        n = i/10
        string = ''
        if n <= 7:
            j = n
        else:
            j = 7
        for k in range(j):
            string += label_s[k]
        label = label_font.render(string, 1, blue)
        screen.blit(label,(10,55))
        screen.blit(skip,(100,290))
        screen.blit(pac,(447,-200+i*3))
        screen.blit(pac_up,(447,900 - i*3))
        pygame.display.flip()
        clock.tick(50)
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (0,0)

def init(fulscreen):
    """
    inicializační procedura
    určí rozměry okna v závislosti na rozlišení obrazovky
    v závisloti na hodnotě proměnné fulscreen se pokusí zapnout celoobrazovkový režim
    """
    global screen
    max = pygame.display.list_modes()[0]
    if max[0] > 1350:
        screen_width = 1350
    else:
        screen_width = max[0]
    if max[1] > 730:
        screen_height = 730
    else:
        screen_height = max[1]

    if not fulscreen:
        screen = pygame.display.set_mode([screen_width,screen_height])
    else:
        try:
            screen = pygame.display.set_mode([screen_width,screen_height],pygame.FULLSCREEN)
        except:
            screen = pygame.display.set_mode([screen_width,screen_height])

def start(player_count):
    """
    procedura inicializující hrací pole, viz dílčí komentáře
    """
    global movable_list,game,pac1,pac2,pac3,pac4,pause,result_list,labels
    #pomocné seznamy
    #texty na obrazovku
    labels = list()
    #seznam pro závěrečné pořadí
    result_list = list()
    #seznam pohybujících se objektů
    movable_list = pygame.sprite.Group()
    monsters_per_player = -1
    try:
        if game:
            monsters_per_player = game.monsters_per_player
    except:
        print ''
    game = Game() #vytvoření nové instance hry
    if monsters_per_player > -1:
        game.monsters_per_player = monsters_per_player
    game.setMazeNo(maze_no)
    # v závislosti na počtu hráčů vytvoří objekty třídy Pac a vloží je do pomocných seznamů
    if player_count > 0:
        pac_pos = game.maze.pac_positions[0]
        pac1 = Pac([0,0],1,ImageStorage(['pac1_up.png','pac2_up.png','pac3_up.png'],['pac1_right.png','pac2_right.png','pac3_right.png'],['pac1_down.png','pac2_down.png','pac3_down.png'],['pac1_left.png','pac2_left.png','pac3_left.png'],),delta_pac,player_names[0],game.compute_position(pac_pos),game,pac_pos[1],pac_pos[0],speed_pac)
        movable_list.add(pac1)
        game.pac_list.append(pac1)
        result_list.append(pac1)
        game.static_list[0] = pac1.name

    if player_count > 1:
        pac_pos = game.maze.pac_positions[1]
        pac2 = Pac([0,0],3,ImageStorage(['pac1_up.png','pac2_up.png','pac3_up.png'],['pac1_right.png','pac2_right.png','pac3_right.png'],['pac1_down.png','pac2_down.png','pac3_down.png'],['pac1_left.png','pac2_left.png','pac3_left.png'],),delta_pac,player_names[1],game.compute_position(pac_pos),game,pac_pos[1],pac_pos[0],speed_pac)
        movable_list.add(pac2)
        result_list.append(pac2)
        game.pac_list.append(pac2)
        game.static_list[1] = pac2.name

    if player_count > 2:
        pac_pos = game.maze.pac_positions[2]
        pac3 = Pac([0,0],1,ImageStorage(['pac1_up.png','pac2_up.png','pac3_up.png'],['pac1_right.png','pac2_right.png','pac3_right.png'],['pac1_down.png','pac2_down.png','pac3_down.png'],['pac1_left.png','pac2_left.png','pac3_left.png'],),delta_pac,player_names[2],game.compute_position(pac_pos),game,pac_pos[1],pac_pos[0],speed_pac)
        movable_list.add(pac3)
        game.pac_list.append(pac3)
        result_list.append(pac3)
        game.static_list[2] = pac3.name

    if player_count > 3:
        pac_pos = game.maze.pac_positions[3]
        pac4 = Pac([0,0],3,ImageStorage(['pac1_up.png','pac2_up.png','pac3_up.png'],['pac1_right.png','pac2_right.png','pac3_right.png'],['pac1_down.png','pac2_down.png','pac3_down.png'],['pac1_left.png','pac2_left.png','pac3_left.png'],),delta_pac,player_names[3],game.compute_position(pac_pos),game,pac_pos[1],pac_pos[0],speed_pac)
        movable_list.add(pac4)
        game.pac_list.append(pac4)
        result_list.append(pac4)
        game.static_list[3] = pac4.name

    #vytvoří seznam objektů třídy ImageStorage
    monster_img_list = list()
    monster_img_list.append(ImageStorage(['purple_up.png','purple2_up.png'],['purple_right.png','purple2_right.png'],['purple_down.png','purple2_down.png'],['purple_left.png','purple2_left.png']))
    monster_img_list.append(ImageStorage(['orange_up.png','orange2_up.png'],['orange_right.png','orange2_right.png'],['orange_down.png','orange2_down.png'],['orange_left.png','orange2_left.png']))
    monster_img_list.append(ImageStorage(['pink_up.png','pink2_up.png'],['pink_right.png','pink2_right.png'],['pink_down.png','pink2_down.png'],['pink_left.png','pink2_left.png']))
    #monster_img_list.append(ImageStorage(['virus_up.png','virus_up2.png'],['virus_down.png','virus_down2.png'],['virus_right.png','virus_right2.png'],['virus_left.png','virus_left2.png']))
    monster_img_list.append(ImageStorage(['cyan_up.png','cyan2_up.png'],['cyan_right.png','cyan2_right.png'],['cyan_down.png','cyan2_down.png'],['cyan_left.png','cyan2_left.png']))
    try:
        #pro každého hráče vytvoří daný počet monster, která jsou na něj zaměřená
        #každé monstrum má náhodně určenou pozici(z možných pozic určených v mapě)
        #tyto pozice se načtou v proceduře initMaze třídy Maze
        #monstra mají různě určené koeficienty náhodnosti a typy (pronásleduje / nadbíhá)
        for player in range(player_count):
            i = 0
            for n in range(game.monsters_per_player):
                i += 1
                hunt_q = i / (game.monsters_per_player * 1.00)
                r = random.randrange(0,4)
                p = random.randrange(len(game.maze.positions))
                p = game.maze.positions[p]
                pos = game.compute_position(p)
                if n % 2 == 0:
                    chaser = True
                else:
                    chaser = False
                if len(game.pac_list) > 0:
                    monster = Monster([1,0],1,monster_img_list[r],delta_monster,'Monster',pos,game,p[1],p[0],speed_monster,hunt_q,game.pac_list[player],chaser)
                    game.monster_list.append(monster)
                    movable_list.add(monster)
                    monster.changePosition()
    except:
        print 'invalid map!'
    pause = False

def play():
    """
    procedurka inicializující muziku
    """
    pygame.mixer.init()
    pygame.mixer.music.load('./music/'+game.song_name)
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)

pygame.init()
#nastavení ikony
icon = pygame.Surface((16,16))
icon.blit(pygame.image.load('./images/pac1_right.png'),(0,0))
pygame.display.set_icon(icon)

#inicializace některých řídících proměnných
fulscreen = True
playing = True
show_menu = True
player_count = 2
maze_no = 1
show_text = False
player_names = ['Pacman','Sadman','Madman','Hackman']
death = pygame.mixer.Sound('./sounds/death.wav')
eatghost = pygame.mixer.Sound('./sounds/eatghost.wav')

#spuštění inicializačních procedur
movie()
init(fulscreen)
pygame.init()
pygame.display.set_caption('Pacmen!','Pacmen!')
clock = pygame.time.Clock()
death.set_volume(0.4)
eatghost.set_volume(0.4)

start(player_count)
pause = True
music = False

#hlavní cyklus programu
while not game.done:
    #zpracování událostí
    for event in pygame.event.get():
        #zavření okna, pauza, restart, vypnutí hudby, fulscreen, menu
        if event.type == pygame.QUIT:
            game.done = True
        if event.type == KEYDOWN:
            if event.key == K_F9:
                if not show_menu:
                    pause = not pause
            elif event.key == K_F5:
                if not show_menu:
                    start(player_count)
            elif event.key == K_F6:
                if music:
                    music = False
                    pygame.mixer.music.pause()
                else:
                    music = True
                    pygame.mixer.music.unpause()
            elif event.key == K_F11:
                fulscreen = not fulscreen
                init(fulscreen)
            elif event.key == K_F10:
                pause = True
                show_menu = True
            elif event.key == K_F12:
                game.done = True
            #změna počtu monster
            elif event.key == K_KP_PLUS:
                game.monsters_per_player += 1
            elif event.key == K_KP_MINUS:
                if game.monsters_per_player > 0:
                    game.monsters_per_player -= 1
            elif event.key == K_RETURN:
                #ošetření položek menu
                if show_menu:
                    action = game.menu.doAction(game)
                    #začátek nové hry
                    if action == 'New game':
                        if (not music) and (game.song_name != '#'):
                            play()
                            music = True
                        elif game.song_name == '#':
                            pygame.mixer.music.pause()
                        playing = True
                        show_menu = False
                        show_text = False
                        start(player_count)
                    #návrat do hry
                    elif action == 'Return':
                        if playing:
                            pause = False
                            show_text = False
                            show_menu = False
                        if (not music) and (game.song_name != '#'):
                            play()
                            music = True
                        elif game.song_name == '#':
                            pygame.mixer.music.pause()
                    #odstranění hráče
                    elif action == 'Remove player':
                        if player_count > 1:
                            player_count -= 1
                            start(player_count)
                            pause = True
                            game.menu.active = 4
                    #přidání hráče
                    elif action == 'Add player':
                        if player_count < 4:
                            player_count +=1
                            start(player_count)
                            pause = True
                            game.menu.active = 3
                    elif action == 'Quit':
                        game.done = True
                    #přejmenování hráčů, volá metodu getName() třídy Menu pro každého hráče
                    #během tohoto procesu není možné reagovat na jiné události
                    elif action == 'Rename players':
                        for i in range(player_count):
                            name = game.menu.getName(screen,player_names[i])
                            player_names[i] = name
                            start(player_count)
                            pause = True
                            game.menu.active = 5
                    #volba mapy
                    elif action == 'Choose a map':
                        show_text = False
                        playing = True
                        player_count = 1
                        start(player_count)
                        pause = True
                        game.menu.active = 2
                        game.menu.list[2] = '< Choose >'
                    elif action == '< Choose >':
                        game.menu.list[2] = 'Choose a map'
                        player_count = 1
                        start(player_count)
                        pause = True
                        game.menu.active = 2
            #ovládání prvního hráče / pohyb v menu
            if event.key == K_UP:
                if show_menu:
                    game.menu.up()
                    game.menu.list[2] = 'Choose a map'
                else:
                    pac1.changeDirection([0,-1],0)
            elif event.key == K_DOWN:
                if show_menu:
                    game.menu.down()
                    game.menu.list[2] = 'Choose a map'
                else:
                    pac1.changeDirection([0,1],2)
            #má smysl i při volbě mapy
            elif event.key == K_RIGHT:
                if game.menu.list[2] == '< Choose >':
                    music = False
                    if maze_no < maze_count:
                        maze_no += 1
                        player_count = 1
                        start(player_count)
                        pause = True
                        game.menu.active = 2
                        game.menu.list[2] = '< Choose >'
                pac1.changeDirection([1,0],1)
            elif event.key == K_LEFT:
                if game.menu.list[2] == '< Choose >':
                    music = False
                    if maze_no > 1:
                        maze_no -= 1
                        player_count = 1
                        start(player_count)
                        pause = True
                        game.menu.active = 2
                        game.menu.list[2] = '< Choose >'
                pac1.changeDirection([-1,0],3)
            #ovládání dalších hráčů
            if player_count > 1:
                if event.key == K_w:
                    pac2.changeDirection([0,-1],0)
                elif event.key == K_s:
                    pac2.changeDirection([0,1],2)
                elif event.key == K_d:
                    pac2.changeDirection([1,0],1)
                elif event.key == K_a:
                    pac2.changeDirection([-1,0],3)
            if player_count > 2:
                if event.key == K_i:
                    pac3.changeDirection([0,-1],0)
                elif event.key == K_k:
                    pac3.changeDirection([0,1],2)
                elif event.key == K_l:
                    pac3.changeDirection([1,0],1)
                elif event.key == K_j:
                    pac3.changeDirection([-1,0],3)
            if player_count > 3:
                if event.key == K_KP8:
                    pac4.changeDirection([0,-1],0)
                elif event.key == K_KP5:
                    pac4.changeDirection([0,1],2)
                elif event.key == K_KP6:
                    pac4.changeDirection([1,0],1)
                elif event.key == K_KP4:
                    pac4.changeDirection([-1,0],3)
    screen.fill(black)

    if playing:
        #vykreslení hrací plochy
        game.draw(screen,player_count)
        #vykreslení případných popisků
        drawLabels(screen)
        if not pause:
            #provedení tahu (pokud není zapauzováno)
            game.move(screen)
        #snězeno všechno krmení, konec hry
        if game.maze.feeds == 0:
            pause = True
            show_menu = True
            show_text = True
        #vykreslení pohybujícíh se objektů
        movable_list.draw(screen)
        #kontrola kolizí pro všechny hráče
        for pac in game.pac_list:
            #získání seznamu kolidujících objektů
            pac_hit_list = pygame.sprite.spritecollide(pac, movable_list, False)
            if len(pac_hit_list) > 1:
                #procházení kolizí
                for hit in pac_hit_list:
                    if hit != pac:
                        #kolize s monstrem
                        if not hit.player:
                            #hráč je v režimu "boss" - monstrum je resetováno na výchozí pozici, hráč si přičte 50 bodů
                            if pac.boss > 0:
                                p = random.randrange(len(game.maze.positions))
                                p = game.maze.positions[p]
                                pos = game.compute_position(p)
                                eatghost.play()
                                pac.score += 50
                                labels.append(['50',[hit.position[0],hit.position[1]],80])
                                hit.position = pos
                                hit.x = p[1]
                                hit.y = p[0]
                                pac.monsters_killed += 1
                            #je-li hráč v normálním režimu, je zabit
                            #odstranění hráče
                            # odstranění na něj zaměřených monster provede funkce die() třídy Pac
                            #přehrání úmrtí Pacmana
                            #v případě, že byl hráč poslední, konec hry
                            else:
                                if (len(game.pac_list) > 0) and (game.pac_list.__contains__(pac)):
                                    movable_list.remove(pac)
                                    game.pac_list.remove(pac)
                                    death.play()
                                    pac.die(movable_list)
                                    playDeath(screen,pac.position,80,0)
                                if len(game.pac_list) == 0:
                                    pause = True
                                    show_text = True
                                    show_menu = True
                        #kolize dvou hráčů
                        else:
                            #ani jeden z hráčů není boss
                            if (pac.boss == 0) and (hit.boss == 0):
                                #odstranění hráče s menším skóre
                                #odstranění na něj zaměřených monster provede funkce die() třídy Pac
                                #přehrání úmrtí Pacmana
                                #hráč s vyšším skóre si připočte 80 bodů
                                if pac.score > hit.score:
                                    movable_list.remove(hit)
                                    game.pac_list.remove(hit)
                                    death.play()
                                    hit.die(movable_list)
                                    pac.score += 80
                                    labels.append(['80',[hit.position[0],hit.position[1]],80])
                                    pac.players_killed += 1
                                    playDeath(screen,hit.position,80,0)
                                elif hit.score > pac.score:
                                    movable_list.remove(pac)
                                    death.play()
                                    game.pac_list.remove(pac)
                                    pac.die(movable_list)
                                    hit.score += 80
                                    labels.append(['80',[pac.position[0],pac.position[1]],80])
                                    hit.players_killed += 1
                                    playDeath(screen,pac.position,80,0)
    #40 fps
    clock.tick(40)
    #případné zobrazení menu
    if show_menu:
        game.showMenu(screen,player_names,player_count)
        if show_text:
            showText(screen)
    #zobrazení změn
    pygame.display.flip()

pygame.quit()