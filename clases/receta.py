import pygame
from configuracion import *

def cargar_sprite(ruta):
    imagen =  pygame.image.load(ruta).convert_alpha()
    return imagen

class Receta:
    def __init__(self, nombre, ingredientes):
        self.nombre = nombre
        self.ingredientes = ingredientes
        self.puntos = len(ingredientes) * PUNTOS_POR_INGREDIENTE
        self.tiempo_max = len(ingredientes) * TIEMPO_POR_INGREDIENTE + TIEMPO_BASE_RECETA
        self.tiempo_actual = 0
        self.veces_expirada = 0
        self.sprite = cargar_sprite(f'sprites/{nombre}.png')

    def seguir_chef(self, chef):
        self.x = chef.hitbox.centerx - 8
        self.y = chef.hitbox.top + 42
    
    def dibujar(self, pantalla):
        pantalla.blit(self.sprite, (self.x, self.y))
