import pygame
import random
from configuracion import *
from clases.chef import Chef
from clases.receta import Receta
from clases.estacion import Horno, MesaCocina, Barra
from clases.cocina import Cocina

mapa = [
    "wwwwwwwwwwwwwwww",
    "w..............w",
    "w...aaaaa......w",
    "w..............w",
    "w....hhhhh.....w",
    "w..............w",
    "we.e.wwwww.e.e.w",
    "w....wmcmw.....w",
    "w....wwwww.....w",
    "w..............w",
    "wb.b.b.b.b.....w",
    "wwwwwwwwwwwwwwww",
]

TILES_SOLIDOS = ('w', 'a', 'h', 'e', 'b', 'm', 'c')

despensas = {
    'a': 'masa',
    'h': 'salsa',
    'e': 'queso',
    # pepperoni y jamon van en dispensas separadas
}

# mapa completo con todas las dispensas
mapa = [
    "wwwwwwwwwwwwwwww",#1
    "w........pp..jjw",#2
    "w..............w",#3
    "w..............w",#4
    "w..wccwttwccw..w",#5
    "w..............w",#6
    "wa............aw",#7
    "wa....mwmwm...aw",#8
    "w..............w",#9
    "wq.............w",#10
    "wq..hh..bbbbb..w",#11
    "wwwwwwwwwwwwwwww",#12
    #1234567890123456
]

TILES_SOLIDOS = ('w', 'a', 'h', 'p', 'j', 'q', 'b', 'm', 'c', 't')

despensas = {
    'a': 'masa',
    'h': 'salsa',
    'p': 'pepperoni',
    'j': 'jamon',
    'q': 'queso',
}

INGREDIENTES_SIN_PREP = ['salsa', 'queso', 'pepperoni', 'jamon']

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
            surface.blit(sprites_tiles['.'], rect)
            if celda in sprites_tiles and celda != '.':
                surface.blit(sprites_tiles[celda], rect)

def cargar_estaciones(mapa, TILE_SIZE):
    estaciones = {
        "m": [],  # mesas
        "c": [],  # hornos
        "b": [],  # barras
    }

    for fila, linea in enumerate(mapa):
        for columna, celda in enumerate(linea):

            x = columna * TILE_SIZE
            y = fila * TILE_SIZE

            if celda == "m":
                estaciones["m"].append(MesaCocina(x, y))

            elif celda == "c":
                estaciones["c"].append(Horno(x, y))

            elif celda == "b":
                estaciones["b"].append(Barra(x, y))

    return estaciones

class Nivel2Escena:
    def __init__(self):
        self.siguiente_estado = None
        self.obstaculos = generar_obstaculos(mapa)

        # sprites del mapa
        self.sprite_tiles = {
            '.': cargar_tile("sprites/piso_pizzeria.png"),
            'w': cargar_tile("sprites/pared_pizzeria.png"),
            'a': cargar_tile("sprites/dispensa_masa.png"),
            'h': cargar_tile("sprites/dispensa_salsa.png"),
            'p': cargar_tile("sprites/dispensa_pepperoni.png"),
            'j': cargar_tile("sprites/dispensa_jamon.png"),
            'q': cargar_tile("sprites/dispensa_queso.png"),
            'm': cargar_tile("sprites/mesa_cocina.png"),
            'c': cargar_tile("sprites/horno.png"),
            'b': cargar_tile("sprites/zona_entrega_pizza.png"),
            't': cargar_tile("sprites/basurero.png"),
        }

        # chefs — mismos sprites del nivel 1
        chefs = [
            Chef(550, 250, True,  1, despensas, INGREDIENTES_SIN_PREP),
            Chef(150, 250, False, 2, despensas, INGREDIENTES_SIN_PREP),
        ]

        estaciones = cargar_estaciones(mapa, TILE_SIZE)

        # estaciones
        mesas = estaciones['m']
        hornos = estaciones['c']
        barras = estaciones['b']

        # recetas posibles
        recetas_posibles = [
            Receta("Pizza Pepperoni", ["masa extendida", "salsa", "queso", "pepperoni"]),
            Receta("Pizza Recursiva", ["masa extendida", "masa extendida", "salsa", "salsa", "queso", "queso"]),
            Receta("Pizza Binaria",   ["masa extendida", "salsa", "queso", "pepperoni", "jamon"]),
        ]

        # cocina
        self.cocina = Cocina(
            chefs, hornos, mesas, barras,
            recetas_posibles, tiempo_total=TIEMPO_NIVEL_2
        )

        # filtro naranja fijo
        self.filtro = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.filtro.fill((255, 140, 0))
        self.filtro.set_alpha(40)

        # fade out
        self.terminado = False
        self.fade_alpha = 0
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surface.fill('#000000')

        # musica
        pygame.mixer.music.load("sonidos/pizzeria_music.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        # efectos de sonido
        self.sonido_recoger     = pygame.mixer.Sound("sonidos/recoger.mp3")
        self.sonido_depositar   = pygame.mixer.Sound("sonidos/depositar.mp3")
        self.sonido_hornear     = pygame.mixer.Sound("sonidos/mezclar.mp3")
        self.sonido_entregar    = pygame.mixer.Sound("sonidos/recoger.mp3")
        self.sonido_error       = pygame.mixer.Sound("sonidos/recoger.mp3")
        self.sonido_cambio_chef = pygame.mixer.Sound("sonidos/cambio_chef.mp3")

    def manejar_eventos(self, evento):
        chefs = self.cocina.chefs
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                self.siguiente_estado = 'Menu'

            # cambio de chef
            if evento.key == pygame.K_TAB:
                self.sonido_cambio_chef.play()
                if chefs[0].activo:
                    chefs[0].desactivar()
                    chefs[1].activo = True
                else:
                    chefs[1].desactivar()
                    chefs[0].activo = True

            # interaccion con E
            if evento.key == pygame.K_e:
                for chef in chefs:
                    if chef.activo:
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

            # hornear con F
            if evento.key == pygame.K_f:
                for chef in chefs:
                    if chef.activo:
                        for horno in self.cocina.shakers:  # hornos viven en shakers
                            hx = horno.x // TILE_SIZE
                            hy = horno.y // TILE_SIZE
                            cx = chef.hitbox.centerx // TILE_SIZE
                            cy = chef.hitbox.centery // TILE_SIZE
                            if (cx == hx and abs(cy - hy) == 1) or (cy == hy and abs(cx - hx) == 1):
                                horno.mezclar()  # mezclar = hornear
                                self.sonido_hornear.play()

            if evento.key == pygame.K_p:
                self.cocina.tiempo_restante = 5 * 60
                                

    def actualizar(self):
        if not self.terminado:
            self.cocina.actualizar(self.obstaculos)

            if self.cocina.tiempo_restante <= 0:
                self.terminado = True
        else:
            self.fade_alpha += VELOCIDAD_FADE
            self.fade_alpha = min(255, self.fade_alpha)
            if self.fade_alpha >= 255:
                pygame.mixer.music.stop()
                self.siguiente_estado = 'Resultados2'

    def dibujar(self, pantalla, font_grande, font_mediana, font_pequena):
        dibujar_mapa(pantalla, mapa, self.sprite_tiles)
        self.cocina.dibujar(pantalla)
        pantalla.blit(self.filtro, (0, 0))
        self.cocina.dibujar_hud(pantalla, font_grande, font_mediana, font_pequena, 'TURING PIZZA')

        if self.terminado:
            self.fade_surface.set_alpha(self.fade_alpha)
            pantalla.blit(self.fade_surface, (0, 0))
