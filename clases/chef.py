import pygame
from configuracion import *
from clases.ingrediente import Ingrediente

def cargar_sprites(ruta):
    imagen =  pygame.image.load(ruta).convert_alpha()
    return pygame.transform.scale(imagen, SPRITE_SIZE)

class Chef:
    def __init__(self, x, y, activo, chef_sprite, despensas, ingredientes_sin_prep):
        self.x = float(x)
        self.y = float(y)
        self.activo = activo
        self.facing = 'down'
        self.moviendose = False
        self.en_mano = None
        self.despensas = despensas
        self.ingredientes_sin_prep = ingredientes_sin_prep
        self.sprites = {
    "down": [
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}01.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}01.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}02.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}03.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}04.png"),
    ],
    "up": [
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}05.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}05.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}06.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}07.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}08.png"),
    ],
    "right": [
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}09.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}10.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}11.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}12.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}13.png"),
    ],
    "left": [
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}14.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}15.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}16.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}17.png"),
        cargar_sprites(f"sprites/Layer 1_sprite_Chef{chef_sprite}18.png"),
    ],
}

        # - hitbox -
        self.hitbox_offset_x = 28
        self.hitbox_offset_y = 10
        self.hitbox_w = 40
        self.hitbox_h = 84
        self.hitbox = pygame.Rect(
            x + self.hitbox_offset_x,
            y + self.hitbox_offset_y, 
            self.hitbox_w, 
            self.hitbox_h)

        self.anim_frame = 0 #0-3(los 4 frames de movimiento)
        self.anim_timer = 0 # contador para cambiar frame

    def manejar_inputs(self, obstaculos, velocidad):
        if not self.activo:
            return
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        # Movimiento
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -velocidad
            self.facing = "up"
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = velocidad
            self.facing = "down"
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -velocidad
            self.facing = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = velocidad
            self.facing = "right"

        if dx != 0 or dy != 0:
            self.moviendose = True
        else:
            self.moviendose = False

        # Mover en X y verificar colision
        self.hitbox.x += dx
        for obs in obstaculos:
            if self.hitbox.colliderect(obs):
                if dx > 0:
                    self.hitbox.right = obs.left # venia desde la izquierda
                elif dx < 0:
                    self.hitbox.left = obs.right # venia desde la derecha
                self.x = float(self.hitbox.x)
        
        # Mover en Y y verificar colision
        self.hitbox.y += dy
        for obs in obstaculos:
            if self.hitbox.colliderect(obs):
                if dy > 0:
                    self.hitbox.bottom = obs.top # venia desde la arriba
                if dy < 0:
                    self.hitbox.top = obs.bottom # venia desde la abajo
                self.y = float(self.hitbox.y)
        
        # La imagen siempre se deriva de la hitbox
        self.x = float(self.hitbox.x - self.hitbox_offset_x)
        self.y = float(self.hitbox.y - self.hitbox_offset_y)
        
               
    def actualizar_animacion(self):
        if self.moviendose == True:
            self.anim_timer += 1
            if self.anim_timer >= DELAY_ANIMACION:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 4
        else:
            # Quieto: resetea al frame idle
            self.anim_frame = 0
            self.anim_timer = 0
    
    def get_sprite(self):
        frames = self.sprites[self.facing]
        if self.moviendose == True:
            return frames[1 + self.anim_frame] # índices 1-4 son los frames
        else:
            return frames[0] # índice 0 es el idle
        
    def interactuar(self, mapa, shakers, licuadoras):
        # posicion actual del chef en el grid
        cx = self.hitbox.centerx // TILE_SIZE
        cy = self.hitbox.centery // TILE_SIZE

        # tile q esta al frente
        if self.facing == 'up':
            tile_frente = mapa[cy-1][cx]
        elif self.facing == 'down':
            tile_frente = mapa[cy+1][cx]
        elif self.facing == 'left':
            tile_frente = mapa[cy][cx-1]
        elif self.facing == 'right':
            tile_frente = mapa[cy][cx+1]

        if tile_frente in self.despensas and self.en_mano is None:
            nombre = self.despensas[tile_frente]
            self.en_mano = Ingrediente(nombre, self.ingredientes_sin_prep)

        # basurero
        if tile_frente == 't':
            self.en_mano = None

        # shaker
        if tile_frente == 'k':
            for shaker in shakers:
                sx = shaker.x // TILE_SIZE
                sy = shaker.y // TILE_SIZE
                if (cx == sx and abs(cy - sy) == 1) or (cy == sy and abs(cx - sx) == 1):
                    # Interactua con el shaker
                    if self.en_mano is not None and shaker.estado != 'mezclando':
                        shaker.depositar(self.en_mano)
                        self.en_mano = None
                    elif self.en_mano is None:
                        resultado = shaker.recoger()
                        if resultado is not None:
                            self.en_mano = resultado 
        # licuadora
        if tile_frente == 'l':
            for licuadora in licuadoras:
                lx = licuadora.x // TILE_SIZE
                ly = licuadora.y // TILE_SIZE
                if (cx == lx and abs(cy - ly) == 1) or (cy == ly and abs(cx - lx) == 1):
                    licuadora.interactuar(self)
                    break
        
    def desactivar(self):
        self.activo = False
        self.moviendose = False
        self.anim_frame = 0
        self.anim_timer = 0

    def dibujar(self, pantalla):
        self.sprite = self.get_sprite()
        pantalla.blit(self.sprite, (int(self.x), int(self.y)))

        # si tiene algo en mano dibuja encima
        if self.en_mano is not None:
            self.en_mano.seguir_chef(self) # el argumento self funciona como el mismo chef (diablo)
            self.en_mano.dibujar(pantalla)

        # pygame.draw.rect(pantalla, "#18e176", self.hitbox, 2)
