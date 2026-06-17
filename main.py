import pygame
import sys
from configuracion import *
from escenas.menu import MenuEscena
from escenas.nivel1 import Nivel1Escena
from escenas.resultados import ResultadosEscena
from escenas.nivel2 import Nivel2Escena
from escenas.nivel3 import Nivel3Escena
from escenas.pantalla_final import PantallaFinalEscena

# == Inicializacion ==
pygame.init()
FONT_GRANDE  = pygame.font.SysFont(FONT_NAME, BIG_FONT)   # tiempo, puntos, nombre nivel
FONT_MEDIANA = pygame.font.SysFont(FONT_NAME, MEDIUM_FONT)   # nombre receta en tarjeta
FONT_PEQUENA = pygame.font.SysFont(FONT_NAME, SMALL_FONT)   # ingredientes en tarjeta

# == Configuracion ==
pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_TITLE) # Pantalla
icono = pygame.image.load("sprites/icono.png")
pygame.display.set_icon(icono) # Icono ventana
reloj = pygame.time.Clock()

# escena 
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
    escena_actual.dibujar(pantalla, FONT_GRANDE, FONT_MEDIANA, FONT_PEQUENA)

    if escena_actual.siguiente_estado == 'Jugando':
        puntos_nivel1 = 0   # reset al empezar de nuevo
        puntos_nivel2 = 0
        puntos_nivel3 = 0
        escena_actual = Nivel1Escena()

    elif escena_actual.siguiente_estado == 'Nivel1':
        puntos_nivel1 = escena_actual.cocina.puntos
        escena_actual = ResultadosEscena(escena_actual.cocina.puntos, 'Nivel2')

    elif escena_actual.siguiente_estado == 'Nivel2':
        escena_actual = Nivel2Escena()

    elif escena_actual.siguiente_estado == 'Resultados2':
        puntos_nivel2 = escena_actual.cocina.puntos
        escena_actual = ResultadosEscena(escena_actual.cocina.puntos, 'Nivel3')

    elif escena_actual.siguiente_estado == 'Nivel3':
        escena_actual = Nivel3Escena()

    elif escena_actual.siguiente_estado == 'Menu':
        escena_actual = MenuEscena()

    elif escena_actual.siguiente_estado == 'Resultados3':
        puntos_nivel3 = escena_actual.cocina.puntos
        escena_actual = ResultadosEscena(escena_actual.cocina.puntos, 'PantallaFinal')

    elif escena_actual.siguiente_estado == 'PantallaFinal':
        escena_actual = PantallaFinalEscena(puntos_nivel1, puntos_nivel2, puntos_nivel3)

    

    # == Actualizar Pantalla
    pygame.display.flip()
    reloj.tick(60) # 60fps


pygame.quit()
sys.exit()

