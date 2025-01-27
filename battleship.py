#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time
import sys
import pygame
import serial  # Importar la biblioteca serial para comunicación con Arduino
from pygame.locals import *
from joystick_control import read_joystick

# Estructura global para rastrear los barcos y sus coordenadas
ship_positions = {}

# Configuración del puerto serie
try:
    arduino = read_joystick()
    print("Arduino conectado exitosamente.")
    arduino_connected = True
except serial.SerialException:
    print("Advertencia: No se pudo conectar al Arduino. Continuando sin joystick.")
    arduino = None
    arduino_connected = False

# Set variables, like screen width and height 

# globals
FPS = 60 #Determines the number of frames per second
REVEALSPEED = 8 #Determines the speed at which the squares reveals after being clicked
WINDOWWIDTH = 800 #Width of game window
WINDOWHEIGHT = 600 #Height of game window
TILESIZE = 40 #Size of the squares in each grid(tile)
MARKERSIZE = 40 #Size of the box which contatins the number that indicates how many ships in this row/col
BUTTONHEIGHT = 20 #Height of a standard button
BUTTONWIDTH = 40 #Width of a standard button
TEXT_HEIGHT = 25 #Size of the text
TEXT_LEFT_POSN = 10 #Where the text will be positioned
BOARDWIDTH = 10 #Number of grids horizontally
BOARDHEIGHT = 10 #Number of grids vertically
DISPLAYWIDTH = 200 #Width of the game board
EXPLOSIONSPEED = 10 #How fast the explosion graphics will play

XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * TILESIZE) - DISPLAYWIDTH - MARKERSIZE) / 2) #x-position of the top left corner of board 
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * TILESIZE) - MARKERSIZE) / 2) #y-position of the top left corner of board

# Colores

BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
GREEN   = (  0, 204,   0)
GRAY    = ( 60,  60,  60)
BLUE    = (  0,  50, 255)
YELLOW  = (255, 255,   0)
DARKGRAY =( 40,  40,  40)
SEA =  (70, 130, 180)
RED = (255, 0, 0)
BGCOLOR = (0, 128, 128)
#Selecciona background
GBG = pygame.image.load("assets/game_background.jpg")


BUTTONCOLOR = SEA
TEXTCOLOR = WHITE
TILECOLOR = SEA
BORDERCOLOR = BLUE
TEXTSHADOWCOLOR = BLUE
SHIPCOLOR = YELLOW
HIGHLIGHTCOLOR = RED

#INICIAR MEZCLADOR DE AUDIO
pygame.mixer.init()
#EFECTO select
select_sound = pygame.mixer.Sound("sound/select.mp3")  # Asegúrate de que el archivo esté en el directorio correcto
select_sound.set_volume(0.5)  # Ajustar el volumen del efecto de sonido
#EFECTO explosión
boom_sound = pygame.mixer.Sound("sound/boom.mp3")
boom_sound.set_volume(0.5)
#EFECTO bomba al agua
fail_sound = pygame.mixer.Sound("sound/fail.mp3")
fail_sound.set_volume(0.5)
#EFECTO victoria
win_sound = pygame.mixer.Sound("sound/win.mp3")
win_sound.set_volume(0.6)

return_to_menu = False
# Función principal
def main():

    global DISPLAYSURF, FPSCLOCK, BASICFONT, HELP_SURF, HELP_RECT, NEW_SURF, \
           NEW_RECT, SHOTS_SURF, SHOTS_RECT, BIGFONT, COUNTER_SURF, \
           COUNTER_RECT, EXPLOSION_IMAGES,X_SURF,X_RECT,B_SURF,B_RECT
    # Inicialización de Pygame
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Battleship')
    FPSCLOCK = pygame.time.Clock()
    BASICFONT = pygame.font.Font("assets/font.ttf", 20)
    BIGFONT = pygame.font.Font("assets/font.ttf", 50)
    # Botones y textos iniciales
    
    HELP_SURF = BASICFONT.render("Ayuda", True, WHITE)
    HELP_RECT = HELP_SURF.get_rect()
    HELP_RECT.topleft = (WINDOWWIDTH - 205, WINDOWHEIGHT -135)

    X_SURF = BASICFONT.render("X", True, BLUE)
    X_RECT = X_SURF.get_rect()
    X_RECT.topleft = (WINDOWWIDTH - 90, WINDOWHEIGHT -132)
    
    NEW_SURF = BASICFONT.render("New Game", True, WHITE)
    NEW_RECT = NEW_SURF.get_rect()
    NEW_RECT.topleft = (WINDOWWIDTH - 205, WINDOWHEIGHT - 200)

    B_SURF = BASICFONT.render("B", True, RED)
    B_RECT = B_SURF.get_rect()
    B_RECT.topleft = (WINDOWWIDTH - 90, WINDOWHEIGHT -200)

    SHOTS_SURF = BASICFONT.render("Ataques: ", True, WHITE)
    SHOTS_RECT = SHOTS_SURF.get_rect()
    SHOTS_RECT.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 348)



    # Cargar imágenes de explosión
    EXPLOSION_IMAGES = [
        pygame.image.load("img/blowup1.png"), pygame.image.load("img/blowup2.png"),
        pygame.image.load("img/blowup3.png"), pygame.image.load("img/blowup4.png"),
        pygame.image.load("img/blowup5.png"), pygame.image.load("img/blowup6.png")
    ]

    
    while not return_to_menu:
        shots_taken = run_game()  # Ejecutar el juego
        show_gameover_screen(shots_taken)  # Pantalla de fin de juego


def run_game():
    revealed_tiles = generate_default_tiles(False)
    main_board = generate_default_tiles(None)
    ship_objs = ['battleship', 'cruiser1', 'cruiser2', 'destroyer1', 'destroyer2',
                 'destroyer3', 'submarine1', 'submarine2', 'submarine3', 'submarine4']
    main_board = add_ships_to_board(main_board, ship_objs)

    xmarkers, ymarkers = set_markers(main_board)
    counter = []  # Contador de ataques
    hits_counter = 0  # Contador de aciertos
    cursor_x, cursor_y = 0, 0  # Posición inicial del cursor
    mousex, mousey = 0, 0  # Para mouse

    aux_tilex = 0  # Auxiliares para sonido, evitan que selección se repita en loop
    aux_tiley = 0
    current_message = ""  # Variable para almacenar el mensaje actual
    message_timer = 0  # Temporizador para mostrar el mensaje por un tiempo limitado
    GBG = pygame.image.load("assets/game_background.jpg")
    while True:
        # Mostrar contador de aciertos
        HITS_SURF = BASICFONT.render(f"Aciertos: {hits_counter}", True, WHITE)
        HITS_RECT = SHOTS_SURF.get_rect()
        HITS_RECT.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 275)

        COUNTER_SURF = BASICFONT.render(str(len(counter)), True, WHITE)
        COUNTER_RECT = SHOTS_SURF.get_rect()
        COUNTER_RECT.topleft = (WINDOWWIDTH - 115, WINDOWHEIGHT - 348)

        DISPLAYSURF.blit(GBG, (0, 0))
        DISPLAYSURF.blit(HELP_SURF, HELP_RECT)
        DISPLAYSURF.blit(X_SURF, X_RECT)
        DISPLAYSURF.blit(B_SURF, B_RECT)
        DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
        DISPLAYSURF.blit(SHOTS_SURF, SHOTS_RECT)
        DISPLAYSURF.blit(COUNTER_SURF, COUNTER_RECT)
        DISPLAYSURF.blit(HITS_SURF, HITS_RECT)
                
        # Crear textos "BATTLESHIP" y "STELIOS"
        GAME_NAME = BASICFONT.render("BATTLESHIP", True, (182, 143, 64))  # Color #b68f40
        GAME_NAME_RECT = GAME_NAME.get_rect()
        GAME_NAME_RECT.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 515)

        GAME_NAME1 = BASICFONT.render("STELIOS", True, (122, 163, 213))  # Color #7aa3d5
        GAME_NAME1_RECT = GAME_NAME1.get_rect()
        GAME_NAME1_RECT.topleft = (WINDOWWIDTH - 180, WINDOWHEIGHT - 500)

        # Dentro del bucle principal en run_game()
        DISPLAYSURF.blit(GAME_NAME, GAME_NAME_RECT)
        DISPLAYSURF.blit(GAME_NAME1, GAME_NAME1_RECT)

        draw_board(main_board, revealed_tiles)
        draw_markers(xmarkers, ymarkers)

        # Mostrar texto estático "Estado"
        estado_surface = BASICFONT.render("Estado", True, WHITE)
        estado_rect = estado_surface.get_rect()
        estado_rect.topleft = (631, 155)  # Posición fija en la parte superior izquierda
        DISPLAYSURF.blit(estado_surface, estado_rect)

        # Mostrar mensaje dinámico debajo de "Estado"
        if current_message and message_timer > 0:
            # Seleccionar color según el mensaje
            if current_message == "Impacto":
                message_color = (255, 255, 0)  # Amarillo
            elif current_message == "Derribado":
                message_color = (255, 0, 0)  # Rojo
            else:
                message_color = WHITE  # Blanco para otros mensajes

            message_surface = BASICFONT.render(current_message, True, message_color)
            message_rect = message_surface.get_rect()
            message_rect.topleft = (628, 182)  # Justo debajo de "Estado"
            DISPLAYSURF.blit(message_surface, message_rect)
            message_timer = 2  # Reducir temporizador

        if not arduino_connected:
            # Apartado para funcionalidad del mouse
            mouse_clicked = False
            check_for_quit()
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    if HELP_RECT.collidepoint(event.pos):
                        DISPLAYSURF.blit(GBG, (0, 0))
                        show_help_screen()
                    elif NEW_RECT.collidepoint(event.pos):
                        main()
                    else:
                        mousex, mousey = event.pos
                        mouse_clicked = True
                elif event.type == MOUSEMOTION:
                    mousex, mousey = event.pos

            tilex, tiley = get_tile_at_pixel(mousex, mousey)

            if tilex is not None and tiley is not None:
                if not revealed_tiles[tilex][tiley]:
                    if tilex != aux_tilex or tiley != aux_tiley:
                        select_sound.play()
                        aux_tilex = tilex
                        aux_tiley = tiley

                    draw_highlight_tile(tilex, tiley)
                if not revealed_tiles[tilex][tiley] and mouse_clicked:
                    resultado = process_attack(main_board, revealed_tiles, tilex, tiley)
                    current_message = resultado  # Actualizar el mensaje actual
                    message_timer = 60  # Mostrar mensaje por 60 cuadros (1 segundo si FPS=60)

                    if resultado == "Impacto" or resultado == "Derribado":  # Incrementar aciertos solo en impacto
                        hits_counter += 1

                    fail_sound.play()
                    reveal_tile_animation(main_board, [(tilex, tiley)])
                    revealed_tiles[tilex][tiley] = True
                    if check_revealed_tile(main_board, [(tilex, tiley)]):
                        left, top = left_top_coords_tile(tilex, tiley)
                        boom_sound.play()
                        blowup_animation((left, top))
                        if check_for_win(main_board, revealed_tiles):
                            counter.append((tilex, tiley))
                            return len(counter)
                    counter.append((tilex, tiley))
            pygame.display.update()
        else:
            joystick_data = read_joystick()
            if joystick_data:
                xValue = joystick_data["x"]
                yValue = joystick_data["y"]
                buttonY = joystick_data["buttonY"]
                buttonB = joystick_data["buttonB"]
                buttonA = joystick_data["buttonA"]
                buttonX = joystick_data["buttonX"]
                buttonSELECT = joystick_data["buttonSELECT"]

                if xValue < 517:
                    select_sound.play()
                    cursor_x = max(cursor_x - 1, 0)
                elif xValue > 518:
                    select_sound.play()
                    cursor_x = min(cursor_x + 1, BOARDWIDTH - 1)
                if yValue > 497:
                    select_sound.play()
                    cursor_y = max(cursor_y - 1, 0)
                elif yValue < 497:
                    select_sound.play()
                    cursor_y = min(cursor_y + 1, BOARDHEIGHT - 1)

                if buttonA == 1:
                    if not revealed_tiles[cursor_x][cursor_y]:
                        resultado = process_attack(main_board, revealed_tiles, cursor_x, cursor_y)
                        current_message = resultado
                        message_timer = 60  # Mostrar mensaje por 60 cuadros

                        if resultado == "Impacto" or resultado == "Derribado":  # Incrementar aciertos solo en impacto
                            hits_counter += 1

                        fail_sound.play()
                        revealed_tiles[cursor_x][cursor_y] = True
                        if check_revealed_tile(main_board, [(cursor_x, cursor_y)]):
                            left, top = left_top_coords_tile(cursor_x, cursor_y)
                            boom_sound.play()
                            blowup_animation((left, top))
                            if check_for_win(main_board, revealed_tiles):
                                counter.append((cursor_x, cursor_y))
                                return len(counter)
                        counter.append((cursor_x, cursor_y))
                draw_highlight_tile(cursor_x, cursor_y)
                pygame.display.update()
                FPSCLOCK.tick(FPS)

                if buttonY == 1:  # Si el botón del joystick está presionado
                    pygame.quit()
                    sys.exit()

                if buttonX:  # Si el botón del joystick está presionado
                    pygame.display.update()
                    show_help_screen()
                    pygame.display.update()
                
                if buttonB:  # Si el botón del joystick está presionado
                    run_game()
                    

               




# A partir de aqui son las funciones auxiliares

def generate_default_tiles(default_value):
    """
    Function generates a list of 10 x 10 tiles. The list will contain tuples
    ('shipName', boolShot) set to their (default_value).
    
    default_value -> boolean which tells what the value to set to
    returns the list of tuples
    """
    default_tiles = [[default_value]*BOARDHEIGHT for i in range(BOARDWIDTH)]
    
    return default_tiles


def blowup_animation(coord):
    """
    Function creates the explosition played if a ship is shot.
    
    coord -> tuple of tile coords to apply the blowup animation
    """
    for image in EXPLOSION_IMAGES: # go through the list of images in the list of pictures and play them in sequence 
        #Determine the location and size to display the image
        image = pygame.transform.scale(image, (TILESIZE+10, TILESIZE+10))
        DISPLAYSURF.blit(image, coord)
        pygame.display.flip()
        FPSCLOCK.tick(EXPLOSIONSPEED) #Determine the delay to play the image with



def check_revealed_tile(board, tile):
    """
    Function checks if a tile location contains a ship piece.
    
    board -> the tiled board either a ship piece or none
    tile -> location of tile
    returns True if ship piece exists at tile location
    """
    return board[tile[0][0]][tile[0][1]] != None



def reveal_tile_animation(board, tile_to_reveal):
    """
    Function creates an animation which plays when the mouse is clicked on a tile,
    and whatever is behind the tile needs to be revealed.
    
    board -> list of board tile tuples ('shipName', boolShot)
    tile_to_reveal -> tuple of tile coords to apply the reveal animation to
    """
    for coverage in range(TILESIZE, -1, -REVEALSPEED):  # Cobertura decrece correctamente
        if coverage < 0:  # Evitar valores negativos
            coverage = 0
        draw_tile_covers(board, tile_to_reveal, coverage)


def draw_tile_covers(board, tile, coverage):
    """
    Function draws the tiles according to a set of variables.
    
    board -> list of board tiles
    tile -> tuple of tile coords to reveal
    coverage -> int; amount of the tile that is covered
    """
    if coverage <= 0:  # Validación para evitar valores inválidos
        return

    left, top = left_top_coords_tile(tile[0][0], tile[0][1])
    ship_texture = pygame.image.load("assets/BARCOHUNDIDO.png")
    water_texture = pygame.image.load("assets/BARCOHUNDIDO.png")
    tile_texture = pygame.image.load("assets/BARCOHUNDIDO.png")

    # Dibuja la textura según el estado del tile
    if check_revealed_tile(board, tile):
        DISPLAYSURF.blit(ship_texture, (left, top))  # Mostrar textura de barco
    else:
        DISPLAYSURF.blit(water_texture, (left, top))  # Mostrar textura de agua

    # Añadir una animación de cobertura parcial
    cover_surface = pygame.Surface((coverage, TILESIZE))
    cover_surface.blit(tile_texture, (0, 0), (0, 0, coverage, TILESIZE))
    DISPLAYSURF.blit(cover_surface, (left, top))

    pygame.display.update()
    FPSCLOCK.tick(FPS)



def check_for_quit():
    """
    Function checks if the user has attempted to quit the game.
    """
    for event in pygame.event.get(QUIT):
        pygame.quit()
        sys.exit()


def check_for_win(board, revealed):
    """
    Function checks if the current board state is a winning state.
    
    board -> the board which contains the ship pieces
    revealed -> list of revealed tiles
    returns True if all the ships are revealed
    """
    for tilex in range(BOARDWIDTH):
        for tiley in range(BOARDHEIGHT):
            if board[tilex][tiley] != None and not revealed[tilex][tiley]: # check if every board with a ship is revealed, return false if not
                return False
    return True


def draw_board(board, revealed):
    """
    Function draws the game board.
    
    board -> list of board tiles
    revealed -> list of revealed tiles
    """
    # Cargar texturas y asegurarse de escalarlas a TILESIZE
    tile_texture = pygame.image.load("assets/water_01.png")
    ship_texture = pygame.image.load("assets/water_03.png")
    water_texture = pygame.image.load("assets/water_04.png")
    
    tile_texture = pygame.transform.scale(tile_texture, (TILESIZE, TILESIZE))
    ship_texture = pygame.transform.scale(ship_texture, (TILESIZE, TILESIZE))
    water_texture = pygame.transform.scale(water_texture, (TILESIZE, TILESIZE))

    for tilex in range(BOARDWIDTH):
        for tiley in range(BOARDHEIGHT):
            left, top = left_top_coords_tile(tilex, tiley)

            # Tile no revelado: siempre usar la textura del tile no revelado
            if not revealed[tilex][tiley]:
                DISPLAYSURF.blit(tile_texture, (left, top))
            else:  # Tile revelado
                if board[tilex][tiley] != None:  # Si hay un barco
                    DISPLAYSURF.blit(ship_texture, (left, top))
                else:  # Si no hay un barco
                    DISPLAYSURF.blit(water_texture, (left, top))

    # Dibujar líneas del tablero
    for x in range(0, (BOARDWIDTH + 1) * TILESIZE, TILESIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x + XMARGIN + MARKERSIZE,
                                                 YMARGIN + MARKERSIZE),
                         (x + XMARGIN + MARKERSIZE, WINDOWHEIGHT - YMARGIN))
    for y in range(0, (BOARDHEIGHT + 1) * TILESIZE, TILESIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (XMARGIN + MARKERSIZE, y +
                                                 YMARGIN + MARKERSIZE),
                         (WINDOWWIDTH - (DISPLAYWIDTH + MARKERSIZE * 2),
                          y + YMARGIN + MARKERSIZE))

        
def set_markers(board):
    """
    Function creates the lists of the markers to the side of the game board which indicates
    the number of ship pieces in each row and column.
    
    board: list of board tiles
    returns the 2 lists of markers with number of ship pieces in each row (xmarkers)
        and column (ymarkers)
    """
    xmarkers = [0 for i in range(BOARDWIDTH)]
    ymarkers = [0 for i in range(BOARDHEIGHT)]
    #Loop through the tiles
    for tilex in range(BOARDWIDTH):
        for tiley in range(BOARDHEIGHT):
            if board[tilex][tiley] != None: #if the tile is a ship piece, then increment the markers 
                xmarkers[tilex] += 1
                ymarkers[tiley] += 1

    return xmarkers, ymarkers


def draw_markers(xlist, ylist):
    """
    Function draws the two list of markers to the side of the board.

    xlist -> list of row markers
    ylist -> list of column markers
    """
    for i in range(len(xlist)): #Draw the x-marker list
        left = i * MARKERSIZE + XMARGIN + MARKERSIZE + (TILESIZE / 3)
        top = YMARGIN
        marker_surf, marker_rect = make_text_objs(str(xlist[i]),
                                                    BASICFONT, TEXTCOLOR)
        marker_rect.topleft = (left, top)
        DISPLAYSURF.blit(marker_surf, marker_rect)
    for i in range(len(ylist)): #Draw the y-marker list
        left = XMARGIN
        top = i * MARKERSIZE + YMARGIN + MARKERSIZE + (TILESIZE / 3)
        marker_surf, marker_rect = make_text_objs(str(ylist[i]), 
                                                    BASICFONT, TEXTCOLOR)
        marker_rect.topleft = (left, top)
        DISPLAYSURF.blit(marker_surf, marker_rect)



def add_ships_to_board(board, ships):
    """
    Coloca barcos en el tablero y registra sus coordenadas en ship_positions.
    """
    global ship_positions
    ship_positions = {}
    new_board = board[:]
    for ship in ships:
        valid_ship_position = False
        while not valid_ship_position:
            xStartpos = random.randint(0, 9)
            yStartpos = random.randint(0, 9)
            isHorizontal = random.randint(0, 1)
            # Extraer el tipo de barco eliminando números del nombre
            ship_type = ''.join([char for char in ship if not char.isdigit()])
            ship_length = {'battleship': 4, 'cruiser': 3, 'destroyer': 2, 'submarine': 1}[ship_type]
            valid_ship_position, ship_coords = make_ship_position(new_board, xStartpos, yStartpos, isHorizontal, ship_length, ship)
            if valid_ship_position:
                for coord in ship_coords:
                    new_board[coord[0]][coord[1]] = ship
                ship_positions[ship] = set(ship_coords)  # Guardar coordenadas como conjunto
    return new_board


def process_attack(board, revealed_tiles, x, y):
    """
    Procesa un ataque en la posición (x, y) del tablero.
    """
    global ship_positions

    if revealed_tiles[x][y]:  # Si ya está revelado
        return "Ya revelado"

    revealed_tiles[x][y] = True  # Revelar la casilla

    if board[x][y] is None:  # Si no hay barco en esta casilla
        return "Agua"

    # Hay un barco en esta casilla
    ship = board[x][y]
    ship_positions[ship].remove((x, y))  # Eliminar coordenada del barco

    if not ship_positions[ship]:  # Si no quedan partes del barco
        del ship_positions[ship]  # Eliminar barco del rastreo
        return "Derribado"
    return "Impacto"




def make_ship_position(board, xPos, yPos, isHorizontal, length, ship):
    """
    Function makes a ship on a board given a set of variables
    
    board -> list of board tiles
    xPos -> x-coordinate of first ship piece
    yPos -> y-coordinate of first ship piece
    isHorizontal -> True if ship is horizontal
    length -> length of ship
    returns tuple: True if ship position is valid and list ship coordinates
    """
    ship_coordinates = [] #the coordinates the ship will occupy
    if isHorizontal:
        for i in range(length):
            if (i+xPos > 9) or (board[i+xPos][yPos] != None) or \
                hasAdjacent(board, i+xPos, yPos, ship): #if the ship goes out of bound, hits another ship, or is adjacent to another ship
                return (False, ship_coordinates) #then return false
            else:
                ship_coordinates.append((i+xPos, yPos))
    else:
        for i in range(length):
            if (i+yPos > 9) or (board[xPos][i+yPos] != None) or \
                hasAdjacent(board, xPos, i+yPos, ship): #if the ship goes out of bound, hits another ship, or is adjacent to another ship
                return (False, ship_coordinates) #then return false        
            else:
                ship_coordinates.append((xPos, i+yPos))
    return (True, ship_coordinates) #ship is successfully added


def hasAdjacent(board, xPos, yPos, ship):
    """
    Funtion checks if a ship has adjacent ships
    
    board -> list of board tiles
    xPos -> x-coordinate of first ship piece
    yPos -> y-coordinate of first ship piece
    ship -> the ship being checked for adjacency
    returns true if there are adjacent ships and false if there are no adjacent ships
    """
    for x in range(xPos-1,xPos+2):
        for y in range(yPos-1,yPos+2):
            if (x in range (10)) and (y in range (10)) and \
                (board[x][y] not in (ship, None)):
                return True
    return False
    
    
def left_top_coords_tile(tilex, tiley):
    """
    Function calculates and returns the pixel of the tile in the top left corner
    
    tilex -> int; x position of tile
    tiley -> int; y position of tile
    returns tuple (int, int) which indicates top-left pixel coordinates of tile
    """
    left = tilex * TILESIZE + XMARGIN + MARKERSIZE
    top = tiley * TILESIZE + YMARGIN + MARKERSIZE
    return (left, top)
    
    
def get_tile_at_pixel(x, y):
    """
    Function finds the corresponding tile coordinates of pixel at top left, defaults to (None, None) given a coordinate.
    
    x -> int; x position of pixel
    y -> int; y position of pixel
    returns tuple (tilex, tiley) 
    """
    for tilex in range(BOARDWIDTH):
        for tiley in range(BOARDHEIGHT):
            left, top = left_top_coords_tile(tilex, tiley)
            tile_rect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tile_rect.collidepoint(x, y):
                return (tilex, tiley)
    return (None, None)
    
    
def draw_highlight_tile(tilex, tiley):
    """
    Function draws the hovering highlight over the tile.
    
    tilex -> int; x position of tile
    tiley -> int; y position of tile
    """
    left, top = left_top_coords_tile(tilex, tiley)
    highlight_texture = pygame.image.load("assets/water_02.png")  # Textura de resaltado
    DISPLAYSURF.blit(highlight_texture, (left, top))

def show_help_screen():
    """
    Function display a help screen until any button is pressed.
    """
    DISPLAYSURF.fill("black")
    pygame.display.update()
    line1_surf, line1_rect = make_text_objs('Deje de presionar X para volver, presiona Y para salir', 
                                            BASICFONT, SHIPCOLOR)
    line1_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT)
    DISPLAYSURF.blit(line1_surf, line1_rect)
    
    line2_surf, line2_rect = make_text_objs(
        'Este es el juego de Battleship.', BASICFONT, TEXTCOLOR)
    line2_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 3)
    DISPLAYSURF.blit(line2_surf, line2_rect)

    line3_surf, line3_rect = make_text_objs('Realiza disparos a los recuadros e intenta acertar', BASICFONT, TEXTCOLOR)
    line3_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 4)
    DISPLAYSURF.blit(line3_surf, line3_rect)

    line4_surf, line4_rect = make_text_objs('a un objetivo (barco), estos estaran distribuidos al azar,', BASICFONT, TEXTCOLOR)
    line4_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 5)
    DISPLAYSURF.blit(line4_surf, line4_rect)

    line5_surf, line5_rect = make_text_objs('los numeros en filas y columnas representan cuantas casillas con barco tienen',
        BASICFONT, TEXTCOLOR)
    line5_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 6)
    DISPLAYSURF.blit(line5_surf, line5_rect)

    line6_surf, line6_rect = make_text_objs('para ganar derriba todos los barcos enemigos en el menor numero de disparos.', BASICFONT, TEXTCOLOR)
    line6_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 7)
    DISPLAYSURF.blit(line6_surf, line6_rect)

    line7_surf, line7_rect = make_text_objs('Para reiniciar la partida, es decir Nueva Partida, presiona B', BASICFONT, TEXTCOLOR)
    line7_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 9)
    DISPLAYSURF.blit(line7_surf, line7_rect)

    line8_surf, line8_rect = make_text_objs('Juego realizado para la asignatura', BASICFONT, (128, 128, 128))
    line8_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 20)
    DISPLAYSURF.blit(line8_surf, line8_rect)

    line8_surf, line8_rect = make_text_objs('Sistemas de comunicaciones', BASICFONT, (128, 128, 128))
    line8_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 21)
    DISPLAYSURF.blit(line8_surf, line8_rect)

    line9_surf, line9_rect = make_text_objs('Por equipo: 9', BASICFONT, (128, 128, 128))
    line9_rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * 22)
    DISPLAYSURF.blit(line9_surf, line9_rect)
    

    if arduino_connected == True:
        joystick_data = read_joystick()
        if joystick_data:  # Si los datos no son None
                xValue = joystick_data["x"]
                yValue = joystick_data["y"]
                buttonY = joystick_data["buttonY"]
                buttonB = joystick_data["buttonB"]
                buttonA = joystick_data["buttonA"]
                buttonX = joystick_data["buttonX"]
                buttonSELECT = joystick_data["buttonSELECT"]

                if buttonB == 1: #Check if the user has pressed keys, if so go back to the game
                    pygame.display.update()
                    FPSCLOCK.tick()
    else: 
        while check_for_keypress() == None: #Check if the user has pressed keys, if so go back to the game
            pygame.display.update()
            FPSCLOCK.tick()

def check_for_keypress():
    """
    Function checks for any key presses by pulling out all KEYDOWN and KEYUP events from queue.
    
    returns any KEYUP events, otherwise return None
    """
    for event in pygame.event.get([KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION]):
        if event.type in (KEYDOWN, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEMOTION):
            continue
        return event.key
    return None

    
def make_text_objs(text, font, color):
    """
    Function creates a text.
    
    text -> string; content of text
    font -> Font object; face of font
    color -> tuple of color (red, green blue); colour of text
    returns the surface object, rectangle object
    """
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def show_gameover_screen(shots_fired):
    win_sound.play()
    """
    Function displays a victory screen when the user has successfully hit every ship piece.
    
    shots_fired -> the number of shots taken before the game is over
    """
    
    # Cargar la imagen de fondo para la pantalla de victoria
    victory_bg = pygame.image.load("assets/victory_background.jpg")
    victory_bg = pygame.transform.scale(victory_bg, (WINDOWWIDTH, WINDOWHEIGHT))  # Escalar al tamaño de la ventana
    DISPLAYSURF.blit(victory_bg, (0, 0))

    # Mostrar los textos de victoria

    titleSurf, titleRect = make_text_objs('¡Felicidades! Has ganado.', BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int((WINDOWWIDTH / 2)-3), int((WINDOWHEIGHT / 2) - 50)-3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    titleSurf, titleRect = make_text_objs('¡Felicidades! Has ganado.', BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) - 50)
    DISPLAYSURF.blit(titleSurf, titleRect)

    shotsSurf, shotsRect = make_text_objs(f'Tiros realizados: {shots_fired}', BASICFONT, TEXTSHADOWCOLOR)
    shotsRect.center = (int((WINDOWWIDTH / 2) - 3 ), int((WINDOWHEIGHT / 2) + 20)-3)
    DISPLAYSURF.blit(shotsSurf, shotsRect)

    shotsSurf, shotsRect = make_text_objs(f'Tiros realizados: {shots_fired}', BASICFONT, WHITE)
    shotsRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 20)
    DISPLAYSURF.blit(shotsSurf, shotsRect)

    
    pressKeySurf, pressKeyRect = make_text_objs('Presiona una tecla para jugar de nuevo', BASICFONT, TEXTSHADOWCOLOR)
    pressKeyRect.center = ((int(WINDOWWIDTH / 2)-3), int((WINDOWHEIGHT / 2) + 80)-3)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    pressKeySurf, pressKeyRect = make_text_objs('Presiona una tecla para jugar de nuevo', BASICFONT, WHITE)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 80)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    
    pygame.display.update()

    # Bucle de espera para reiniciar o salir
    waiting = True
    while waiting:
        if arduino_connected:
            joystick_data = read_joystick()
            if joystick_data and joystick_data["buttonA"]:  # Botón A presionado
                waiting = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False  # Salir del bucle para iniciar una nueva partida

        FPSCLOCK.tick(FPS)

    # Reiniciar el juego al salir del bucle
    main()


if __name__ == "__main__":
    main()
