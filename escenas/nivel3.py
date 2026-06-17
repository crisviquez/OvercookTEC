import pygame
import random
from configuracion import *
from clases.chef import Chef
from clases.receta import Receta
from clases.estacion import CocinaLeña, OllaArrocera, TablaPicar, BarraCasita
from clases.cocina import Cocina

mapa = [
    "wwwwwwwwwwwwwwww", 
    "w..aa..tt..ee..w",  
    "w..............w", 
    "wff..hh..ss..rrw", 
    "w..............w",  
    "w.pp..ll.......w",  
    "w..............w",  
    "w..oz.oz.......w",  
    "w..............w",  
    "w.cc..cc.......w", 
    "wb.b.b.b.b.....w",  
    "wwwwwwwwwwwwwwww",  
]

mapa = [
    "wwwwwwwwwwwwwwww", 
    "ww.aahhggssee.ww",  
    "wf............rw", 
    "wf............rw", 
    "w..............w",  
    "wwpp...tt...llww",  
    "wv............vw",  
    "wv.oz......oz.vw",  
    "wv............vw",  
    "wv............vw", 
    "w..bbbbbbbbbb..w",  
    "wwwwwwwwwwwwwwww",  
]

TILES_SOLIDOS = ('w', 'a', 't', 'e', 'f', 'h', 's', 'r',
                 'p', 'l', 'o', 'z', 'v', 'b', 'g')

despensas = {
    'a': 'arroz',
    'g': 'tomate',
    'e': 'huevo',
    'f': 'frijoles negros',
    'h': 'frijoles rojos',
    's': 'salchichon',
    'r': 'chicharron',
    'p': 'platano',
    'l': 'lechuga',
}

INGREDIENTES_SIN_PREP = [
    'frijoles negros', 'frijoles rojos',
    'salchichon', 'chicharron', 'platano', 'lechuga',
    'papas tostadas'
]

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
        'o': [],   # ollas arroceras
        'z': [],   # tablas de picar
        'v': [],   # cocinas de leña
        'b': [],   # barras entrega
    }
    for fila, linea in enumerate(mapa):
        for columna, celda in enumerate(linea):
            x = columna * TILE_SIZE
            y = fila * TILE_SIZE
            if celda == 'o':
                estaciones['o'].append(OllaArrocera(x, y))
            elif celda == 'z':
                estaciones['z'].append(TablaPicar(x, y))
            elif celda == 'v':
                estaciones['v'].append(CocinaLeña(x, y))
            elif celda == 'b':
                estaciones['b'].append(BarraCasita(x, y))
    return estaciones

class Nivel3Escena:
    def __init__(self):
        self.siguiente_estado = None
        self.obstaculos = generar_obstaculos(mapa)

        self.sprite_tiles = {
            '.': cargar_tile("sprites/piso_casita.png"),
            'w': cargar_tile("sprites/pared_casita.png"),
            'a': cargar_tile("sprites/dispensa_arroz.png"),
            'g': cargar_tile("sprites/dispensa_tomate.png"),
            'e': cargar_tile("sprites/dispensa_huevo.png"),
            'f': cargar_tile("sprites/dispensa_frijoles_negros.png"),
            'h': cargar_tile("sprites/dispensa_frijoles_rojos.png"),
            's': cargar_tile("sprites/dispensa_salchichon.png"),
            'r': cargar_tile("sprites/dispensa_chicharron.png"),
            'p': cargar_tile("sprites/dispensa_platano.png"),
            'l': cargar_tile("sprites/dispensa_lechuga.png"),
            'o': cargar_tile("sprites/olla_arrocera_normal.png"),
            'z': cargar_tile("sprites/tabla_picar_normal.png"),
            'v': cargar_tile("sprites/cocina_lena_normal.png"),
            'b': cargar_tile("sprites/zona_entrega_casita.png"),
            't': cargar_tile("sprites/basurero.png")
        }

        chefs = [
            Chef(400, 300, True,  1, despensas, INGREDIENTES_SIN_PREP),
            Chef(250, 300, False, 2, despensas, INGREDIENTES_SIN_PREP),
        ]

        estaciones = cargar_estaciones(mapa, TILE_SIZE)
        ollas     = estaciones['o']   # van donde van las licuadoras
        tablas    = estaciones['z']   # van donde van las licuadoras también
        cocinas   = estaciones['v']   # van donde van los shakers
        barras    = estaciones['b']

        # combinamos ollas y tablas en licuadoras
        # ya que ambas funcionan igual (proceso automático)
        procesadoras = ollas + tablas

        recetas_posibles = [
            Receta("Pinto", [
                "arroz cocido", "frijoles negros", "huevo picado", "salchichon"
            ]),
            Receta("Chifrijo", [
                "arroz cocido", "frijoles rojos", "tomate picado", "chicharron"
            ]),
            Receta("Sopa Negra", [
                "arroz cocido", "frijoles negros", "huevo picado"
            ]),
            Receta("Casado", [
                "arroz cocido", "frijoles negros", "salchichon", "lechuga", "tomate picado"
            ]),
        ]

        self.cocina = Cocina(
            chefs,
            cocinas,       # shakers = cocinas de leña
            procesadoras,  # licuadoras = ollas + tablas
            barras,
            recetas_posibles,
            tiempo_total=TIEMPO_NIVEL_3
        )

        # filtro verdoso
        self.filtro = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.filtro.fill((50, 180, 80))
        self.filtro.set_alpha(30)

        # fade out
        self.terminado = False
        self.fade_alpha = 0
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surface.fill('#000000')

        # musica
        pygame.mixer.music.load("sonidos/casita_music.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        # sonidos
        self.sonido_recoger     = pygame.mixer.Sound("sonidos/recoger.mp3")
        self.sonido_depositar   = pygame.mixer.Sound("sonidos/depositar.mp3")
        self.sonido_cocinar     = pygame.mixer.Sound("sonidos/mezclar.mp3")
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

            # interaccion E
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

            # cocinar con F
            if evento.key == pygame.K_f:
                for chef in chefs:
                    if chef.activo:
                        for cocina in self.cocina.shakers:  # cocinas viven en shakers
                            kx = cocina.x // TILE_SIZE
                            ky = cocina.y // TILE_SIZE
                            cx = chef.hitbox.centerx // TILE_SIZE
                            cy = chef.hitbox.centery // TILE_SIZE
                            if (cx == kx and abs(cy - ky) == 1) or (cy == ky and abs(cx - kx) == 1):
                                cocina.mezclar()
                                self.sonido_cocinar.play()

            # debug — skip tiempo
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
                self.siguiente_estado = 'Resultados3'
                PTS_PANTALLA_3 = self.cocina.puntos

    def dibujar(self, pantalla, font_grande, font_mediana, font_pequena):
        dibujar_mapa(pantalla, mapa, self.sprite_tiles)
        self.cocina.dibujar(pantalla)
        pantalla.blit(self.filtro, (0, 0))
        self.cocina.dibujar_hud(pantalla, font_grande, font_mediana, font_pequena, 'CASITA FORESTAL')

        if self.terminado:
            self.fade_surface.set_alpha(self.fade_alpha)
            pantalla.blit(self.fade_surface, (0, 0))
