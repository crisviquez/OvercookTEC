import pygame
import sys

pygame.init()
WIDTH = 640
HEIGHT = 480
pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock() #controla FPS

VELOCIDAD = 10
DELAY_ANIMACIONES=8
SPRITE_SIZE = (96,96)

# Cargar sprites
def cargar_sprites(ruta):
    imagen =  pygame.image.load(ruta).convert_alpha()
    return pygame.transform.scale(imagen, SPRITE_SIZE)

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
        self.anim_frame = 0 # 0-3 (los 4 frames de movimiento)
        self.anim_timer = 0 # contador para cambiar frame

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            if self.y > 0-7:
                dy = -VELOCIDAD
            self.facing = "up"
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if self.y < (HEIGHT - SPRITE_SIZE[0]):
                dy = VELOCIDAD
            self.facing = "down"
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            if self.x > 0-22:
                dx = -VELOCIDAD
            self.facing = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if self.x < WIDTH-78:
                dx = VELOCIDAD
            self.facing = "right"

        if dx == 0 or dy == 0:
            self.moving = False
        else:
            self.moving = True
        self.x += dx
        self.y += dy

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
        
Rectangulo = pygame.Rect(300,200,96,96)

def dibujar_cuadradito():
    pygame.draw.rect(pantalla, '#ffffff', Rectangulo)

player = Player(WIDTH // 2, HEIGHT // 2)

# Bucle del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    player.handle_input()
    player.update_animation()

    pantalla.fill((30, 30, 30))
    player.draw(pantalla)


    pygame.display.flip()
    clock.tick(60)