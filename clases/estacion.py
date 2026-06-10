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
            print('Capacidad maxima alcanzada')

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
