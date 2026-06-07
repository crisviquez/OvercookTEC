import pygame
from configuracion import *

def cargar_sprite(ruta):
    imagen =  pygame.image.load(ruta).convert_alpha()
    return imagen

class Ingrediente:
    def __init__(self, nombre, ingredientes_sin_prep):
        self.nombre = nombre

        # posicion (sigue al chef)
        self.x = 0
        self.y = 0

        # Estado de los ingredientes
        if nombre in ingredientes_sin_prep:
            self.estado = 'listo'
        else:
            self.estado = 'crudo'

        # sprites segun estado
        if self.estado == 'listo':
            self.sprites = { 'listo':   cargar_sprite(f"sprites/ing_{nombre}.png")}
        else:
            self.sprites = {
                'crudo':     cargar_sprite(f"sprites/ing_{nombre}_crudo.png"),
                'preparado': cargar_sprite(f"sprites/ing_{nombre}_preparado.png"),
                }

    def seguir_chef(self, chef):
        self.x = chef.hitbox.centerx - 8
        self.y = chef.hitbox.top + 42

    def dibujar(self, pantalla):
        sprite_actual = self.sprites[self.estado]
        pantalla.blit(sprite_actual, (self.x, self.y))

    def preparar(self):
        pass

class Desecho:
    def __init__(self):
        self.nombre = 'desecho'
        self.x = 0
        self.y = 0
        self.sprite = cargar_sprite("sprites/ing_desecho.png")

    def seguir_chef(self, chef):
        self.x = chef.hitbox.centerx - 8
        self.y = chef.hitbox.top + 42

    def dibujar(self, pantalla):
        pantalla.blit(self.sprite, (self.x, self.y))
