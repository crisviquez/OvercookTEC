import pygame
import math
import random
from configuracion import *
from clases.chef import Chef
from clases.receta import Receta
from clases.estacion import *

mapa = [
    "wwwwwwwwwwwwwwww",  
    "wb...h.p.h.p...w",  
    "wb.............w",  
    "wb...........s.w",  
    "wb....l.l......w",  
    "wb....wwww...r.w",  
    "wb....k.kw.....w",  
    "wb.......w...r.w",  
    "wb......tw.....w",  
    "wb.......w.....w",  
    "wb..c.n..w.c.n.w",  
    "wwwwwwwwwwwwwwww",  
]
TILES_SOLIDOS = ('w', 'b', 'h', 'p', 'l', 'k', 'r', 's', 'c', 'n', 't')
despensas = {
    'r': 'coca cola',
    's': 'smirnoff',
    'c': 'cacique',
    'n': 'ron',
    'p': 'piña',
    'h': 'hielo',
    }
INGREDIENTES_SIN_PREP = ['hielo', 'coca cola', 'smirnoff', 'ron', 'cacique']

# --- Funciones del mapa ---
def generar_obstaculos(mapa):
    obstaculos = []
    for fila_idx, fila in enumerate(mapa):
        for col_idx, celda in enumerate(fila):
            if celda in TILES_SOLIDOS:
                obstaculos.append(pygame.Rect(
                    col_idx * TILE_SIZE,
                    fila_idx * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                ))
    return obstaculos

def cargar_tile(ruta):
    imagen = pygame.image.load(ruta).convert_alpha()
    return pygame.transform.scale(imagen, (TILE_SIZE, TILE_SIZE))

def dibujar_mapa(surface, mapa, sprites_tiles):
    for fila_idx, fila in enumerate(mapa):
        for col_idx, celda in enumerate(fila):
            rect = pygame.Rect(
                col_idx * TILE_SIZE,
                fila_idx * TILE_SIZE,
                TILE_SIZE, TILE_SIZE
            )
            # primero dibuja el piso siempre
            surface.blit(sprites_tiles['.'], rect)
            
            # si el tile tiene sprite propio, lo dibuja encima
            if celda in sprites_tiles and celda != '.':
                surface.blit(sprites_tiles[celda], rect)

class Nivel1Escena:
    def __init__(self):
        self.siguiente_estado = None # no quiero cambiar de escena
        self.obstaculos = generar_obstaculos(mapa)
        self.chef1 = Chef(200,200, True, 1)
        self.chef2 = Chef(100,200, False, 2)
        self.recetas = [
    Receta("Ron con Cola",  ["ron", "coca cola", "hielo"]),
    Receta("Piña Colada",   ["piña licuada", "cacique", "hielo"]),
    Receta("Smirnoff",      ["smirnoff", "hielo"]),
]
        self.shakers = [
            Shaker(6 * TILE_SIZE, 6 * TILE_SIZE), 
            Shaker(8 * TILE_SIZE, 6 * TILE_SIZE)]
        self.licuadoras = [
            Licuadora(6 * TILE_SIZE, 4 * TILE_SIZE), 
            Licuadora(8 * TILE_SIZE, 4 * TILE_SIZE)]
        self.filtro = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.filtro.fill((0, 0, 50))
        self.filtro.set_alpha(128)
        self.tiempo_filtro = 0
        self.musica = ["sonidos/cali_music_1.mp3", "sonidos/cali_music_2.mp3"]
        self.sprite_tiles = {
    '.': cargar_tile("sprites/piso.png"),
    'w': cargar_tile("sprites/pared.png"),
    'b': cargar_tile("sprites/barra.png"),
    'h': cargar_tile("sprites/hielera.png"),
    'p': cargar_tile("sprites/refri_pina.png"),
    'l': cargar_tile("sprites/licuadora.png"),
    'k': cargar_tile("sprites/shaker.png"),
    'r': cargar_tile("sprites/refri_coca.png"),
    's': cargar_tile("sprites/refri_smirnoff.png"),
    'c': cargar_tile("sprites/estante_cacique.png"),
    'n': cargar_tile("sprites/estante_ron.png"),
    't': cargar_tile('sprites/basurero.png')
}       # musica
        pygame.mixer.music.load(random.choice(self.musica))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop() # parar musica
                self.siguiente_estado = 'Menu' # cambiar estado
            if evento.key == pygame.K_TAB:
                if self.chef1.activo:
                    self.chef1.desactivar()
                    self.chef2.activo = True
                else:
                    self.chef2.desactivar()
                    self.chef1.activo = True

            if evento.key == pygame.K_e:
                if self.chef1.activo:
                    self.chef1.interactuar(mapa, despensas, INGREDIENTES_SIN_PREP, self.shakers, self.licuadoras)
                else:
                    self.chef2.interactuar(mapa, despensas, INGREDIENTES_SIN_PREP, self.shakers, self.licuadoras)
            
            if evento.key == pygame.K_f:
                if self.chef1.activo:
                    chef_activo = self.chef1
                else:
                    chef_activo = self.chef2
                for shaker in self.shakers:
                    # verifica si el chef está frente a este shaker específico
                    sx = shaker.x // TILE_SIZE
                    sy = shaker.y // TILE_SIZE
                    cx = chef_activo.hitbox.centerx // TILE_SIZE
                    cy = chef_activo.hitbox.centery // TILE_SIZE
                    if (cx == sx and abs(cy - sy) == 1) or (cy == sy and abs(cx - sx) == 1):
                        shaker.mezclar()

        
    

    def actualizar(self):
        self.chef1.manejar_inputs(self.obstaculos, 4)
        self.chef2.manejar_inputs(self.obstaculos, 4)
        self.chef1.actualizar_animacion()
        self.chef2.actualizar_animacion()

        for shaker in self.shakers:
            shaker.actualizar(self.recetas)
        for licuadora in self.licuadoras:
            licuadora.actualizar()
        
        # EFECTO PULSO
        self.tiempo_filtro += 0.2 # (mas alto = mas rapido)
        alfa_dinamico = int(120 + math.sin(self.tiempo_filtro) * 30)
        self.filtro.set_alpha(alfa_dinamico)

    def dibujar(self, pantalla, font):
        dibujar_mapa(pantalla, mapa, self.sprite_tiles)
        self.chef1.dibujar(pantalla)
        self.chef2.dibujar(pantalla)
        for shaker in self.shakers:
            shaker.dibujar(pantalla)
        for licuadora in self.licuadoras:
            licuadora.dibujar(pantalla)

        # Filtro    
        pantalla.blit(self.filtro, (0,0))
        texto = font.render("LA CALI (esc)", False, "#ffffff")
        pantalla.blit(texto, (10, 10))
        
