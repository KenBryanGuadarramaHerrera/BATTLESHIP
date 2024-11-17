import pygame
import sys
import time
from battleship import main
from button import Button
from joystick_control import read_joystick  # Importar la función del joystick

pygame.init()

# Configuración de la pantalla
SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Menu")

BG = pygame.image.load("assets/Background.png")

def get_font(size):  # Retorna una fuente en el tamaño deseado
    return pygame.font.Font("assets/font.ttf", size)

def play():
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black")

        PLAY_TEXT = get_font(45).render("This is the PLAY screen.", True, "White")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        PLAY_BACK = Button(image=None, pos=(640, 460), 
                           text_input="BACK", font=get_font(75), base_color="White", hovering_color="Green")

        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)

        joystick_input = read_joystick()  # Leer datos del joystick
        if joystick_input:
            if joystick_input["buttonA"]:  # Si el botón del joystick está presionado
                main_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(640, 460), 
                              text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        joystick_input = read_joystick()  # Leer datos del joystick
        if joystick_input:
            if joystick_input["buttonA"]:  # Si el botón del joystick está presionado
                main_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    cursor_index = 0  # Índice para manejar la selección en el menú
    menu_items = ["PLAY", "OPTIONS", "QUIT"]  # Opciones del menú
    buttons = [
        Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250),
               text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White"),
        Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400),
               text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White"),
        Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550),
               text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
    ]

    while True:
        SCREEN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("BATTLESHIP", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for i, button in enumerate(buttons):
            if i == cursor_index:
                button.changeColor((0, 0))  # Fuerza el cambio de color para el botón seleccionado
            else:
                button.changeColor((-1, -1))  # No seleccionado
            button.update(SCREEN)

        joystick_input = read_joystick()  # Leer datos del joystick
        if joystick_input:
            # Navegación con el joystick
            if joystick_input["y"] < 492:  # Joystick hacia arriba
                cursor_index = (cursor_index - 1) % len(menu_items)
                time.sleep(0.2)  # Pausa para evitar múltiples cambios rápidos
            elif joystick_input["y"] > 502:  # Joystick hacia abajo
                cursor_index = (cursor_index + 1) % len(menu_items)
                time.sleep(0.2)  # Pausa para evitar múltiples cambios rápidos

            # Selección con el botón del joystick
            if joystick_input["buttonA"]:
                selected_option = menu_items[cursor_index]
                if selected_option == "PLAY":
                    main()
                elif selected_option == "OPTIONS":
                    options()
                elif selected_option == "QUIT":
                    pygame.quit()
                    sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button, action in zip(buttons, [main, options, sys.exit]):
                    if button.checkForInput(MENU_MOUSE_POS):
                        action()

        pygame.display.update()

main_menu()
