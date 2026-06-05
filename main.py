import pygame
import sys
from configuracion import * 
from escenas.menu import MenuEscena
from escenas.nivel1 import Nivel1Escena

# == Inicializacion ==
pygame.init()
FONT = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

# == Configuracion ==
pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_TITLE) # Pantalla
icono = pygame.image.load("sprites/icono.png")
pygame.display.set_icon(icono) # Icono ventana
reloj = pygame.time.Clock()

# escena - testing
escena_actual = MenuEscena()


# == BUCLE PRINCIPAL ==
ejecutando = True
while ejecutando:

    #  == Modulo de Eventos Globales ==
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        # input del jugador
        escena_actual.manejar_eventos(evento)
    
    # == Modulo de Logica y Dibujo ==
    escena_actual.actualizar()
    escena_actual.dibujar(pantalla, FONT)

    if escena_actual.siguiente_estado == 'Jugando':
        escena_actual = Nivel1Escena()
    if escena_actual.siguiente_estado == 'Menu':
        escena_actual = MenuEscena()

    
    # == Actualizar Pantalla
    pygame.display.flip()
    reloj.tick(60) # 60fps


pygame.quit()
sys.exit()