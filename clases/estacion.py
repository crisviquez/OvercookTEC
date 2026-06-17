import pygame
from configuracion import *
from clases.ingrediente import Desecho

def cargar_tile(ruta):
    imagen = pygame.image.load(ruta).convert_alpha()
    return pygame.transform.scale(imagen, (TILE_SIZE, TILE_SIZE))


# CLASE BASE
class Estacion:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.sprite = sprite

    def interactuar(self, chef):
        pass  # cada hija sobreescribe esto

    def actualizar(self):
        pass  # cada hija sobreescribe esto

    def dibujar(self, pantalla):
        pantalla.blit(self.sprite, (self.x, self.y))



class Shaker(Estacion):
    def __init__(self, x, y):
        super().__init__(x, y, cargar_tile("sprites/shaker_normal.png"))
        self.ingredientes = []
        self.estado = 'vacio'
        self.timer_mezcla = 0
        self.resultado = None
        self.limite = LIMITE_SHAKER
        self.sprites = {
            'vacio':     cargar_tile("sprites/shaker_normal.png"),
            'cargado':   cargar_tile("sprites/shaker_normal.png"),
            'mezclando': cargar_tile("sprites/shaker_mezclando.png"),
            'listo':     cargar_tile("sprites/shaker_listo.png"),
        }
        # mensaje lleno
        self.mensaje_lleno = ''
        self.timer_mensaje = 0

    def interactuar(self, chef, recetas_disponibles=None):
        if chef.en_mano is not None and self.estado != 'mezclando':
            self.depositar(chef.en_mano)
            chef.en_mano = None
        elif chef.en_mano is None:
            resultado = self.recoger()
            if resultado is not None:
                chef.en_mano = resultado

    def depositar(self, ingrediente):
        if len(self.ingredientes) < self.limite:
            self.ingredientes.append(ingrediente)
            self.estado = 'cargado'
        else:
            self.mensaje_lleno = 'Capacidad maxima'
            self.timer_mensaje = 120 #2sec

    def mezclar(self):
        if self.estado == 'cargado':
            self.estado = 'mezclando'
            self.timer_mezcla = 0

    def actualizar(self, recetas_disponibles):
        if self.estado == 'mezclando':
            self.timer_mezcla += 1
            if self.timer_mezcla >= TIEMPO_MEZCLA:  # 180 frames = 3s a 60fps
                self.estado = 'listo'
                self.resultado = self.comparar_con_recetas(recetas_disponibles)

        #timer mensaje lleno
        if self.timer_mensaje > 0:
            self.timer_mensaje -= 1
            if self.timer_mensaje <= 0:
                self.mensaje_lleno = ''

    def comparar_con_recetas(self, recetas_disponibles):
        nombres_shaker = sorted([i.nombre for i in self.ingredientes])
        for receta in recetas_disponibles:
            nombres_receta = sorted(receta.ingredientes)
            if nombres_shaker == nombres_receta:
                return receta
        return Desecho()

    def recoger(self):
        if self.estado == 'listo':
            resultado = self.resultado
            self.ingredientes = []
            self.resultado = None
            self.estado = 'vacio'
            return resultado
        return None

    def dibujar_ingredientes(self, pantalla):
        for i, ingrediente in enumerate(self.ingredientes):
            x = self.x + i * 16
            y = self.y
            sprite_actual = ingrediente.sprites[ingrediente.estado]
            pantalla.blit(sprite_actual, (x, y))

    def dibujar(self, pantalla):
        sprite_actual = self.sprites[self.estado]
        pantalla.blit(sprite_actual, (self.x, self.y))
        if self.estado == 'cargado':
            self.dibujar_ingredientes(pantalla)
        if self.estado == 'listo':
            pantalla.blit(self.resultado.sprite, (self.x + 16, self.y + 8))

        # barra de progreso de mezcla
        if self.estado == 'mezclando':
            progreso = self.timer_mezcla / 180
            ancho_barra = int(TILE_SIZE * progreso)
            pygame.draw.rect(pantalla, '#333333', (self.x, self.y - 10, TILE_SIZE, 6), border_radius=3)
            pygame.draw.rect(pantalla, '#44aaff', (self.x, self.y - 10, ancho_barra, 6), border_radius=3)

        # mensaje mostrar llenado
        if self.mensaje_lleno:
            font = pygame.font.SysFont(FONT_NAME, SMALL_FONT)
            texto = font.render(self.mensaje_lleno, False, "#ba7373")
            pantalla.blit(texto, (self.x - 28, self.y - 12))





class Licuadora(Estacion):
    def __init__(self, x, y):
        super().__init__(x, y, cargar_tile("sprites/licuadora.png"))
        self.ingrediente = None # solo tiene uno a la vez
        self.estado = 'vacia'
        self.timer = 0
        self.ingredientes_aceptados = ['piña']  # solo acepta piña por ahora
        self.sprites = {
            'vacia':       cargar_tile("sprites/licuadora.png"),
            'procesando':  cargar_tile("sprites/licuadora_procesando.png"),
            'lista':       cargar_tile("sprites/licuadora_lista.png"),
        }

    def interactuar(self, chef):
        # depositar si el chef tiene algo en mano y la licuadora está vacía
        if chef.en_mano is not None and self.estado == 'vacia':
            if chef.en_mano.nombre in self.ingredientes_aceptados:
                self.ingrediente = chef.en_mano
                chef.en_mano = None
                self.estado = 'procesando'
                self.timer = 0

        # recoger si ya está lista
        elif chef.en_mano is None and self.estado == 'lista':
            chef.en_mano = self.ingrediente
            self.ingrediente = None
            self.estado = 'vacia'

    def actualizar(self):
        if self.estado == 'procesando':
            self.timer += 1
            if self.timer >= TIEMPO_LICUADO:  # 3 segundos a 60fps
                self.ingrediente.estado = 'preparado'
                self.ingrediente.nombre = 'piña licuada'  
                self.estado = 'lista' # cambia estado del ingrediente

    def dibujar(self, pantalla):
        sprite_actual = self.sprites[self.estado]
        pantalla.blit(sprite_actual, (self.x, self.y))

        # dibuja el ingrediente encima si está procesando o lista
        if self.estado in ('procesando', 'lista') and self.ingrediente is not None:
            sprite_ing = self.ingrediente.sprites[self.ingrediente.estado]
            pantalla.blit(sprite_ing, (self.x + 16, self.y + 8))

            # barra de progreso de mezcla
        if self.estado == 'procesando':
            progreso = self.timer / 180
            ancho_barra = int(TILE_SIZE * progreso)
            pygame.draw.rect(pantalla, '#333333', (self.x, self.y - 10, TILE_SIZE, 6), border_radius=3)
            pygame.draw.rect(pantalla, '#44aaff', (self.x, self.y - 10, ancho_barra, 6), border_radius=3)



class Barra(Estacion):
    def __init__(self, x, y):
        super().__init__(x, y, cargar_tile("sprites/barra.png"))

    def interactuar(self, chef, recetas_activas, puntos_jugador):
        # solo acepta recetas terminadas, no ingredientes sueltos
        if chef.en_mano is None:
            return
        
        from clases.receta import Receta
        if not isinstance(chef.en_mano, Receta):
            return

        # compara con recetas activas
        for receta in recetas_activas:
            if chef.en_mano.nombre == receta.nombre:
                puntos_jugador += receta.puntos
                recetas_activas.remove(receta)
                chef.en_mano = None
                return puntos_jugador

        # si no coincide con ninguna — desaparece igual
        chef.en_mano = None
        return puntos_jugador
    
class MesaCocina(Estacion):
    def __init__(self, x, y):
        super().__init__(x, y, cargar_tile("sprites/mesa_cocina_normal.png"))
        self.ingrediente = None
        self.estado = 'vacia'
        self.timer = 0
        self.ingredientes_aceptados = ['masa']
        self.sprites = {
            'vacia':      cargar_tile("sprites/mesa_cocina_normal.png"),
            'procesando': cargar_tile("sprites/mesa_cocina_procesando.png"),
            'lista':      cargar_tile("sprites/mesa_cocina_lista.png"),
        }

    def interactuar(self, chef):
        if chef.en_mano is not None and self.estado == 'vacia':
            if chef.en_mano.nombre in self.ingredientes_aceptados:
                self.ingrediente = chef.en_mano
                chef.en_mano = None
                self.estado = 'procesando'
                self.timer = 0
        elif chef.en_mano is None and self.estado == 'lista':
            chef.en_mano = self.ingrediente
            self.ingrediente = None
            self.estado = 'vacia'

    def actualizar(self):
        if self.estado == 'procesando':
            self.timer += 1
            if self.timer >= TIEMPO_MEZCLA:
                self.ingrediente.estado = 'preparado'
                self.ingrediente.nombre = 'masa extendida'
                self.estado = 'lista'

    def dibujar(self, pantalla):
        sprite_actual = self.sprites[self.estado]
        pantalla.blit(sprite_actual, (self.x, self.y))
        if self.estado in ('procesando', 'lista') and self.ingrediente is not None:
            sprite_ing = self.ingrediente.sprites[self.ingrediente.estado]
            pantalla.blit(sprite_ing, (self.x, self.y - TILE_SIZE))
        if self.estado == 'procesando':
            progreso = self.timer / TIEMPO_MEZCLA
            ancho_barra = int(TILE_SIZE * progreso)
            pygame.draw.rect(pantalla, '#333333', (self.x, self.y - 10, TILE_SIZE, 6), border_radius=3)
            pygame.draw.rect(pantalla, '#ff9900', (self.x, self.y - 10, ancho_barra, 6), border_radius=3)


class Horno(Estacion):
    def __init__(self, x, y):
        super().__init__(x, y, cargar_tile("sprites/horno_normal.png"))
        self.ingredientes = []
        self.estado = 'vacio'
        self.timer_horneado = 0
        self.resultado = None
        self.limite = LIMITE_HORNO
        self.sprites = {
            'vacio':      cargar_tile("sprites/horno_normal.png"),
            'cargado':    cargar_tile("sprites/horno_normal.png"),
            'horneando':  cargar_tile("sprites/horno_procesando.png"),
            'listo':      cargar_tile("sprites/horno_listo.png"),
        }
        # mensaje lleno
        self.mensaje_lleno = ''
        self.timer_mensaje = 0

    def interactuar(self, chef, recetas_disponibles=None):
        if chef.en_mano is not None and self.estado != 'horneando':
            self.depositar(chef.en_mano)
            chef.en_mano = None
        elif chef.en_mano is None:
            resultado = self.recoger()
            if resultado is not None:
                chef.en_mano = resultado

    def depositar(self, ingrediente):
        if len(self.ingredientes) < self.limite:
            self.ingredientes.append(ingrediente)
            self.estado = 'cargado'
        else:
            self.mensaje_lleno = 'Capacidad maxima'
            self.timer_mensaje = 120 #2sec

    def mezclar(self):  # mezclar = hornear
        if self.estado == 'cargado':
            self.estado = 'horneando'
            self.timer_horneado = 0

    def actualizar(self, recetas_disponibles):
        if self.estado == 'horneando':
            self.timer_horneado += 1
            if self.timer_horneado >= TIEMPO_MEZCLA:
                self.estado = 'listo'
                self.resultado = self.comparar_con_recetas(recetas_disponibles)
        #timer mensaje lleno
        if self.timer_mensaje > 0:
            self.timer_mensaje -= 1
            if self.timer_mensaje <= 0:
                self.mensaje_lleno = ''

    def comparar_con_recetas(self, recetas_disponibles):
        nombres_horno = sorted([i.nombre for i in self.ingredientes])
        for receta in recetas_disponibles:
            nombres_receta = sorted(receta.ingredientes)
            if nombres_horno == nombres_receta:
                return receta
        return Desecho()

    def recoger(self):
        if self.estado == 'listo':
            resultado = self.resultado
            self.ingredientes = []
            self.resultado = None
            self.estado = 'vacio'
            return resultado
        return None

    def dibujar_ingredientes(self, pantalla):
        for i, ingrediente in enumerate(self.ingredientes):
            sprite_actual = ingrediente.sprites[ingrediente.estado]
            sprite_actual = pygame.transform.scale(sprite_actual, (16,16))
            if i >= 3:
                x = self.x + (i-3) * 16
                y = self.y + 16
            else:
                x = self.x + i * 16
                y = self.y
            pantalla.blit(sprite_actual, (x, y))

    def dibujar(self, pantalla):
        sprite_actual = self.sprites[self.estado]
        pantalla.blit(sprite_actual, (self.x, self.y))
        if self.estado == 'cargado':
            self.dibujar_ingredientes(pantalla)
        elif self.estado == 'listo' and self.resultado is not None:
            pantalla.blit(self.resultado.sprite, (self.x + 8, self.y + 8))
        elif self.estado == 'horneando':
            progreso = self.timer_horneado / TIEMPO_MEZCLA
            ancho_barra = int(TILE_SIZE * progreso)
            pygame.draw.rect(pantalla, '#333333', (self.x, self.y - 10, TILE_SIZE, 6), border_radius=3)
            pygame.draw.rect(pantalla, '#ff4400', (self.x, self.y - 10, ancho_barra, 6), border_radius=3)
        # mensaje mostrar llenado
        if self.mensaje_lleno:
            font = pygame.font.SysFont(FONT_NAME, SMALL_FONT)
            texto = font.render(self.mensaje_lleno, False, "#ba7373")
            pantalla.blit(texto, (self.x - 28, self.y - 12))

class OllaArrocera(Estacion):
    def __init__(self, x, y):
        super().__init__(x, y, cargar_tile("sprites/olla_arrocera_normal.png"))
        self.ingrediente = None
        self.estado = 'vacia'
        self.timer = 0
        self.ingredientes_aceptados = ['arroz']
        self.sprites = {
            'vacia':      cargar_tile("sprites/olla_arrocera_normal.png"),
            'procesando': cargar_tile("sprites/olla_arrocera_procesando.png"),
            'lista':      cargar_tile("sprites/olla_arrocera_lista.png"),
        }

    def interactuar(self, chef):
        if chef.en_mano is not None and self.estado == 'vacia':
            if chef.en_mano.nombre in self.ingredientes_aceptados:
                self.ingrediente = chef.en_mano
                chef.en_mano = None
                self.estado = 'procesando'
                self.timer = 0
        elif chef.en_mano is None and self.estado == 'lista':
            chef.en_mano = self.ingrediente
            self.ingrediente = None
            self.estado = 'vacia'

    def actualizar(self):
        if self.estado == 'procesando':
            self.timer += 1
            if self.timer >= TIEMPO_MEZCLA:
                self.ingrediente.estado = 'preparado'
                self.ingrediente.nombre = 'arroz cocido'
                self.estado = 'lista'

    def dibujar(self, pantalla):
        sprite_actual = self.sprites[self.estado]
        pantalla.blit(sprite_actual, (self.x, self.y))
        if self.estado in ('procesando', 'lista') and self.ingrediente is not None:
            sprite_ing = self.ingrediente.sprites[self.ingrediente.estado]
            pantalla.blit(sprite_ing, (self.x + 8, self.y - TILE_SIZE))
        if self.estado == 'procesando':
            progreso = self.timer / TIEMPO_MEZCLA
            ancho_barra = int(TILE_SIZE * progreso)
            pygame.draw.rect(pantalla, '#333333', (self.x, self.y - 10, TILE_SIZE, 6), border_radius=3)
            pygame.draw.rect(pantalla, '#44cc44', (self.x, self.y - 10, ancho_barra, 6), border_radius=3)


class TablaPicar(Estacion):
    def __init__(self, x, y):
        super().__init__(x, y, cargar_tile("sprites/tabla_picar_normal.png"))
        self.ingrediente = None
        self.estado = 'vacia'
        self.timer = 0
        self.ingredientes_aceptados = ['tomate', 'huevo']
        self.sprites = {
            'vacia':      cargar_tile("sprites/tabla_picar_normal.png"),
            'procesando': cargar_tile("sprites/tabla_picar_procesando.png"),
            'lista':      cargar_tile("sprites/tabla_picar_lista.png"),
        }
        # nombres resultantes segun ingrediente
        self.nombres_resultado = {
            'tomate': 'tomate picado',
            'huevo':  'huevo picado',
        }

    def interactuar(self, chef):
        if chef.en_mano is not None and self.estado == 'vacia':
            if chef.en_mano.nombre in self.ingredientes_aceptados:
                self.ingrediente = chef.en_mano
                chef.en_mano = None
                self.estado = 'procesando'
                self.timer = 0
        elif chef.en_mano is None and self.estado == 'lista':
            chef.en_mano = self.ingrediente
            self.ingrediente = None
            self.estado = 'vacia'

    def actualizar(self):
        if self.estado == 'procesando':
            self.timer += 1
            if self.timer >= TIEMPO_MEZCLA:
                nombre_original = self.ingrediente.nombre
                self.ingrediente.estado = 'preparado'
                self.ingrediente.nombre = self.nombres_resultado[nombre_original]
                self.estado = 'lista'

    def dibujar(self, pantalla):
        sprite_actual = self.sprites[self.estado]
        pantalla.blit(sprite_actual, (self.x, self.y))
        if self.estado in ('procesando', 'lista') and self.ingrediente is not None:
            sprite_ing = self.ingrediente.sprites[self.ingrediente.estado]
            pantalla.blit(sprite_ing, (self.x + 8, self.y - TILE_SIZE))
        if self.estado == 'procesando':
            progreso = self.timer / TIEMPO_MEZCLA
            ancho_barra = int(TILE_SIZE * progreso)
            pygame.draw.rect(pantalla, '#333333', (self.x, self.y - 10, TILE_SIZE, 6), border_radius=3)
            pygame.draw.rect(pantalla, '#cc8800', (self.x, self.y - 10, ancho_barra, 6), border_radius=3)


class CocinaLeña(Estacion):
    def __init__(self, x, y):
        super().__init__(x, y, cargar_tile("sprites/cocina_lena_normal.png"))
        self.ingredientes = []
        self.estado = 'vacio'
        self.timer_coccion = 0
        self.resultado = None
        self.limite = LIMITE_HORNO
        self.sprites = {
            'vacio':     cargar_tile("sprites/cocina_lena_normal.png"),
            'cargado':   cargar_tile("sprites/cocina_lena_normal.png"),
            'cocinando': cargar_tile("sprites/cocina_lena_cocinando.png"),
            'listo':     cargar_tile("sprites/cocina_lena_lista.png"),
        }
        self.mensaje_lleno = ''
        self.timer_mensaje = 0

    def interactuar(self, chef, recetas_disponibles=None):
        if chef.en_mano is not None and self.estado != 'cocinando':
            self.depositar(chef.en_mano)
            chef.en_mano = None
        elif chef.en_mano is None:
            resultado = self.recoger()
            if resultado is not None:
                chef.en_mano = resultado

    def depositar(self, ingrediente):
        if len(self.ingredientes) < self.limite:
            self.ingredientes.append(ingrediente)
            self.estado = 'cargado'
        else:
            self.mensaje_lleno = 'Capacidad maxima'
            self.timer_mensaje = 120

    def mezclar(self):  # mezclar = cocinar
        if self.estado == 'cargado':
            self.estado = 'cocinando'
            self.timer_coccion = 0

    def actualizar(self, recetas_disponibles):
        if self.estado == 'cocinando':
            self.timer_coccion += 1
            if self.timer_coccion >= TIEMPO_MEZCLA:
                self.estado = 'listo'
                self.resultado = self.comparar_con_recetas(recetas_disponibles)
        if self.timer_mensaje > 0:
            self.timer_mensaje -= 1
            if self.timer_mensaje <= 0:
                self.mensaje_lleno = ''

    def comparar_con_recetas(self, recetas_disponibles):
        nombres_cocina = sorted([i.nombre for i in self.ingredientes])
        for receta in recetas_disponibles:
            nombres_receta = sorted(receta.ingredientes)
            if nombres_cocina == nombres_receta:
                return receta
        return Desecho()

    def recoger(self):
        if self.estado == 'listo':
            resultado = self.resultado
            self.ingredientes = []
            self.resultado = None
            self.estado = 'vacio'
            return resultado
        return None

    def dibujar_ingredientes(self, pantalla):
        for i, ingrediente in enumerate(self.ingredientes):
            sprite_actual = ingrediente.sprites[ingrediente.estado]
            sprite_actual = pygame.transform.scale(sprite_actual, (16, 16))
            if i >= 3:
                x = self.x + (i - 3) * 16
                y = self.y + 16
            else:
                x = self.x + i * 16
                y = self.y
            pantalla.blit(sprite_actual, (x, y))

    def dibujar(self, pantalla):
        sprite_actual = self.sprites[self.estado]
        pantalla.blit(sprite_actual, (self.x, self.y))
        if self.estado == 'cargado':
            self.dibujar_ingredientes(pantalla)
        elif self.estado == 'listo' and self.resultado is not None:
            pantalla.blit(self.resultado.sprite, (self.x + 8, self.y + 8))
        elif self.estado == 'cocinando':
            progreso = self.timer_coccion / TIEMPO_MEZCLA
            ancho_barra = int(TILE_SIZE * progreso)
            pygame.draw.rect(pantalla, '#333333', (self.x, self.y - 10, TILE_SIZE, 6), border_radius=3)
            pygame.draw.rect(pantalla, '#cc4400', (self.x, self.y - 10, ancho_barra, 6), border_radius=3)
        if self.mensaje_lleno:
            font = pygame.font.SysFont(FONT_NAME, SMALL_FONT)
            texto = font.render(self.mensaje_lleno, False, "#ba7373")
            pantalla.blit(texto, (self.x - 28, self.y - 12))


class BarraCasita(Estacion):
    def __init__(self, x, y):
        super().__init__(x, y, cargar_tile("sprites/zona_entrega_casita.png"))
