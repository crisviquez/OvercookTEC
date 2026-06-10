import pygame
import math
import random
from configuracion import *
from clases.chef import Chef
from clases.receta import Receta
from clases.estacion import *
from clases.cocina import Cocina

mapa = [
    "wwwwwwwwwwwwwwww",  
    "wb...h.p.h.p...w",  
    "wb.............w",  
    "wb...........s.w",  
    "wb...wlwlw.....w",  
    "wb...wwwww...r.w",  
    "wb...wkwkw.....w",  
    "wb...........r.w",  
    "wb.............w",  
    "wb.............w",  
    "wb..c.n.tt.c.n.w",  
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
        self.siguiente_estado = None
        self.obstaculos = generar_obstaculos(mapa)

        # sprites del mapa
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
            't': cargar_tile("sprites/basurero.png"),
        }

        # chefs
        chefs = [
            Chef(500, 200, True,  1, despensas, INGREDIENTES_SIN_PREP),
            Chef(100, 200, False, 2, despensas, INGREDIENTES_SIN_PREP),
        ]

        # estaciones
        shakers = [
            Shaker(6 * TILE_SIZE, 6 * TILE_SIZE),
            Shaker(8 * TILE_SIZE, 6 * TILE_SIZE),
        ]
        licuadoras = [
            Licuadora(6 * TILE_SIZE, 4 * TILE_SIZE),
            Licuadora(8 * TILE_SIZE, 4 * TILE_SIZE),
        ]
        barras = [
                  Barra(1 * TILE_SIZE, 2 * TILE_SIZE),
                  Barra(1 * TILE_SIZE, 3 * TILE_SIZE),
                  Barra(1 * TILE_SIZE, 4 * TILE_SIZE),
                  Barra(1 * TILE_SIZE, 5 * TILE_SIZE),
                  Barra(1 * TILE_SIZE, 6 * TILE_SIZE),
                  Barra(1 * TILE_SIZE, 7 * TILE_SIZE),
                  Barra(1 * TILE_SIZE, 8 * TILE_SIZE),
                  Barra(1 * TILE_SIZE, 9 * TILE_SIZE),
                  Barra(1 * TILE_SIZE, 10 * TILE_SIZE)]



        # recetas posibles
        recetas_posibles = [
            Receta("Ron con Cola", ["ron", "coca cola", "hielo"]),
            Receta("Piña Colada",  ["piña licuada", "cacique", "hielo"]),
            Receta("Smirnoff",     ["smirnoff", "hielo"]),
        ]

        # cocina — administra todo
        self.cocina = Cocina(
            chefs, shakers, licuadoras, barras,
            recetas_posibles, tiempo_total=TIEMPO_NIVEL_1  # 4 minutos
        )

        # efecto visual
        self.filtro = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.filtro.fill((0, 0, 50))
        self.filtro.set_alpha(128)
        self.tiempo_filtro = 0

        # efecto visual fade out
        self.terminado = False
        self.fade_alpha = 0
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surface.fill('#000000')

        # musica
        self.musica = ["sonidos/cali_music_1.mp3", "sonidos/cali_music_2.mp3"]
        pygame.mixer.music.load(random.choice(self.musica))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        # efectos de sonido
        self.sonido_recoger = pygame.mixer.Sound("sonidos/recoger.mp3")
        self.sonido_recoger.set_volume(0.5)
        self.sonido_depositar = pygame.mixer.Sound("sonidos/depositar.mp3")
        self.sonido_depositar.set_volume(0.5)
        self.sonido_mezclar = pygame.mixer.Sound("sonidos/mezclar.mp3")
        self.sonido_mezclar.set_volume(0.5)
        self.sonido_entregar = pygame.mixer.Sound("sonidos/recoger.mp3")
        self.sonido_entregar.set_volume(0.5)
        self.sonido_error = pygame.mixer.Sound("sonidos/recoger.mp3")
        self.sonido_error.set_volume(0.5)
        self.sonido_cambio_chef = pygame.mixer.Sound("sonidos/cambio_chef.mp3")
        self.sonido_cambio_chef.set_volume(0.5)

    def manejar_eventos(self, evento):
        chefs = self.cocina.chefs
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop() # parar musica
                self.siguiente_estado = 'Menu' # cambiar estado

            # cambio de chef
            if evento.key == pygame.K_TAB:
                self.sonido_cambio_chef.play()
                if chefs[0].activo:
                    chefs[0].desactivar()
                    chefs[1].activo = True
                else:
                    chefs[1].desactivar()
                    chefs[0].activo = True

            # interaccion
            if evento.key == pygame.K_e:
                for chef in chefs:
                    if chef.activo:
                        # chequea si está frente a la barra
                        cx = chef.hitbox.centerx // TILE_SIZE
                        cy = chef.hitbox.centery // TILE_SIZE
                        if chef.facing == 'up':    tile_frente = mapa[cy-1][cx]
                        elif chef.facing == 'down': tile_frente = mapa[cy+1][cx]
                        elif chef.facing == 'left': tile_frente = mapa[cy][cx-1]
                        elif chef.facing == 'right': tile_frente = mapa[cy][cx+1]

                        if tile_frente == 'b':
                            entregado = False
                            for barra in self.cocina.barras:
                                bx = barra.x // TILE_SIZE
                                by = barra.y // TILE_SIZE
                                if (cx == bx and abs(cy - by) == 1) or (cy == by and abs(cx - bx) == 1):
                                    entregado = self.cocina.entregar_receta(chef)
                                    break

                            if entregado:
                                self.sonido_entregar.play()
                            else:
                                self.sonido_error.play()
                        else:
                            en_mano_antes = chef.en_mano
                            chef.interactuar(mapa, self.cocina.shakers, self.cocina.licuadoras)
                            if chef.en_mano is not None and en_mano_antes is None:
                                self.sonido_recoger.play()
                            elif chef.en_mano is None and en_mano_antes is not None:
                                self.sonido_depositar.play()
            
            # mezclar shaker
            if evento.key == pygame.K_f:
                for chef in chefs:
                    if chef.activo:
                        for shaker in self.cocina.shakers:
                            sx = shaker.x // TILE_SIZE
                            sy = shaker.y // TILE_SIZE
                            cx = chef.hitbox.centerx // TILE_SIZE
                            cy = chef.hitbox.centery // TILE_SIZE
                            if (cx == sx and abs(cy - sy) == 1) or (cy == sy and abs(cx - sx) == 1):
                                shaker.mezclar()
                                self.sonido_mezclar.play()
                
            if evento.key == pygame.K_p:
                self.cocina.tiempo_restante = 5 * 60

        
    

    def actualizar(self):
        if not self.terminado:
            self.cocina.actualizar(self.obstaculos)
        
            # EFECTO PULSO
            self.tiempo_filtro += VELOCIDAD_PULSO # (mas alto = mas rapido)
            alfa_dinamico = int(120 + math.sin(self.tiempo_filtro) * 30)
            self.filtro.set_alpha(alfa_dinamico)

            if self.cocina.tiempo_restante <= 0:
                self.terminado = True

        else:
            # fade out
            self.fade_alpha += VELOCIDAD_FADE
            self.fade_alpha = min(255, self.fade_alpha)

            if self.fade_alpha >= 255:
                self.siguiente_estado = 'Nivel1'
                pygame.mixer.music.stop()

             

    def dibujar(self, pantalla, font_grande, font_mediana, font_pequena):
        dibujar_mapa(pantalla, mapa, self.sprite_tiles)
        self.cocina.dibujar(pantalla)
        # Filtro    
        pantalla.blit(self.filtro, (0,0))

        self.cocina.dibujar_hud(pantalla, font_grande, font_mediana, font_pequena, 'LA CALI')

        if self.terminado:
            self.fade_surface.set_alpha(self.fade_alpha)
            pantalla.blit(self.fade_surface, (0, 0))
        
