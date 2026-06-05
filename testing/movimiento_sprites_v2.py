import pygame
import sys

pygame.init()
WIDTH = 768
HEIGHT = 576
pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock() #controla FPS

VELOCIDAD = 4
DELAY_ANIMACIONES=8
SPRITE_SIZE = (96,96)

TILE_SIZE = 48  # tamaño de cada casilla en pixeles

mapa_1 = [
    "wwwwwwwwwwwwwwww",
    "w..............w",
    "w..............w",
    "w..............w",
    "w.....w...w....w",
    "w..............w",
    "w..............w",
    "w..............w",
    "w..............w",
    "w....w.........w",
    "w.w.www.w.www..w",
    "wwwwwwwwwwwwwwww"
]
mapa = []
for fila in mapa_1:
    mapa.append(list(fila))

print(mapa)

# Cargar sprites
def cargar_sprites(ruta):
    imagen =  pygame.image.load(ruta).convert_alpha()
    return pygame.transform.scale(imagen, SPRITE_SIZE)


def generar_mapa(mapa):
    paredes = []
    for fila_idx, fila in enumerate(mapa):
        for col_idx, celda in enumerate(fila):
            if celda == "w":
                rect = pygame.Rect(
                    col_idx * TILE_SIZE,
                    fila_idx * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                paredes.append(rect)
    return paredes

COLOR_PISO  = (80,  70,  60)
COLOR_PARED = (50,  50,  80)

def dibujar_mapa(surface, mapa):
    for fila_idx, fila in enumerate(mapa):
        for col_idx, celda in enumerate(fila):
            rect = pygame.Rect(
                col_idx * TILE_SIZE,
                fila_idx * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
            if celda == ".":
                pygame.draw.rect(surface, COLOR_PISO, rect)
            elif celda == "w":
                pygame.draw.rect(surface, COLOR_PARED, rect)

obstaculos = generar_mapa(mapa)

sprites = {
    "down": [
        cargar_sprites("testing/sprites/L1.png"),
        cargar_sprites("testing/sprites/L1.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef102.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef103.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef104.png"),
    ],
    "up": [
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef105.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef105.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef106.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef107.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef108.png"),
    ],
    "right": [
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef109.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef110.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef111.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef112.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef113.png"),
    ],
    "left": [
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef114.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef115.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef116.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef117.png"),
        cargar_sprites("testing/sprites/Layer 1_sprite_Chef118.png"),
    ],
}

# --- Estado del jugador ---
class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.facing = "down" # direcciOn actual
        self.moving = False

        self.hitbox_offset_x = 24
        self.hitbox_offset_y = 10
        self.hitbox_w = 48
        self.hitbox_h = 88
        self.hitbox = pygame.Rect(
            x + self.hitbox_offset_x,
            y + self.hitbox_offset_y, 
            self.hitbox_w, 
            self.hitbox_h)

        self.anim_frame = 0 # 0-3 (los 4 frames de movimiento)
        self.anim_timer = 0 # contador para cambiar frame

    def handle_input(self, obstaculos):
        global VELOCIDAD
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -VELOCIDAD
            self.facing = "up"
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = VELOCIDAD
            self.facing = "down"
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -VELOCIDAD
            self.facing = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = VELOCIDAD
            self.facing = "right"

        if keys[pygame.K_f]:
            VELOCIDAD += 0.1

        # Mover en X y verificar colision
        self.hitbox.x += dx
        for obs in obstaculos:
            if self.hitbox.colliderect(obs):
                if dx > 0:
                    self.hitbox.right = obs.left # venia desde la izquierda
                if dx < 0:
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

    def update_animation(self):
        if self.moving == True:
            self.anim_timer += 1
            if self.anim_timer >= DELAY_ANIMACIONES:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 4
        else:
            # Quieto: resetea al frame idle
            self.anim_frame = 0
            self.anim_timer = 0

    def get_sprite(self):
        frames = sprites[self.facing]
        if self.moving == True:
            return frames[1 + self.anim_frame] # índices 1-4 son los frames
        else:
            return frames[0] # índice 0 es el idle

    def draw(self, surface):
        sprite = self.get_sprite()
        surface.blit(sprite, (int(self.x), int(self.y)))
        
        pygame.draw.rect(surface, "#18e176", self.hitbox, 2)
        
player = Player(WIDTH // 2, HEIGHT // 2)

# Bucle del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    player.handle_input(obstaculos)
    player.update_animation()

    pantalla.fill((0,0,0))
    dibujar_mapa(pantalla, mapa)

    # Dibujar obstaculos
    player.draw(pantalla)
    for obs in obstaculos:
        pygame.draw.rect(pantalla, '#f1f1f1', obs)


    pygame.display.flip()
    clock.tick(60)