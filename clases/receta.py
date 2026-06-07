import pygame

def cargar_sprite(ruta):
    imagen =  pygame.image.load(ruta).convert_alpha()
    return imagen

class Receta:
    def __init__(self, nombre, ingredientes):
        self.nombre = nombre
        self.ingredientes = ingredientes
        self.puntos = len(ingredientes) * 50
        self.tiempo_max = len(ingredientes) * 20 + 10
        self.tiempo_actual = 0
        self.sprite = cargar_sprite(f'sprites/{nombre}.png')

    def seguir_chef(self, chef):
        self.x = chef.hitbox.centerx - 8
        self.y = chef.hitbox.top + 42
    
    def dibujar(self, pantalla):
        pantalla.blit(self.sprite, (self.x, self.y))
