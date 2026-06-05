import pygame
import sys

pygame.init()
WIDTH = 768
HEIGHT = 576
pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('OVERCOOK')
FONT = pygame.font.SysFont('Minecraft', 30)
clock = pygame.time.Clock() #controla FPS

VELOCIDAD = 4
VELOCIDAD_BASE = VELOCIDAD
DELAY_ANIMACIONES=8
SPRITE_SIZE = (96,96)
score_testing = 0

# 2. Configurar variables del timer
TIEMPO_TOTAL = 120 # en segundos
tiempo_inicio = pygame.time.get_ticks()

TILE_SIZE = 48  # tamaño de cada casilla en pixeles

mapa_1 = [
    "wwwwwwwwwwwwwwww",
    "w..............w",
    "w..............w",
    "w..............w",
    "w..e.e.........w",
    "w..............w",
    "w...........ff.w",
    "w.......ffffff.w",
    "w.e..e.........w",
    "w..............w",
    "w.w.www.w.www..w",
    "wwwwwwwwwwwwwwww"
]

mapa = []
for fila in mapa_1:
    mapa.append(list(fila))

TILES_SOLIDOS = ('w', 'c', 'e')

def cargar_tile(ruta):
    imagen = pygame.image.load(ruta).convert_alpha()
    return pygame.transform.scale(imagen, (TILE_SIZE, TILE_SIZE))

tile_sprites = {
    "c": cargar_tile("sprites/tile_e.png"),
    "e": cargar_tile("sprites/tile_e.png"),
    "f": cargar_tile("sprites/tile_f.png"),
}

# Cargar sprites
def cargar_sprites(ruta):
    imagen =  pygame.image.load(ruta).convert_alpha()
    return pygame.transform.scale(imagen, SPRITE_SIZE)


def generar_mapa(mapa):
    paredes = []
    for fila_idx, fila in enumerate(mapa):
        for col_idx, celda in enumerate(fila):
            if celda in TILES_SOLIDOS:
                 paredes.append(pygame.Rect(
                    col_idx * TILE_SIZE,
                    fila_idx * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                ))
    return paredes

COLORES = {
    ".": (80,  70,  60),
    "w": (50,  50,  80),
    "c": (200, 100,  50),
    "e": (50,  180, 180),
    "f": (255, 220,   0)
}

def dibujar_mapa(surface, mapa):
    for fila_idx, fila in enumerate(mapa):
        for col_idx, celda in enumerate(fila):
            color = COLORES.get(celda, (0, 0, 0))
            rect = pygame.Rect(
                col_idx * TILE_SIZE,
                fila_idx * TILE_SIZE,
                TILE_SIZE, TILE_SIZE
            )
            if celda in tile_sprites:
                # Dibuja el piso debajo primero, luego el sprite encima
                pygame.draw.rect(surface, COLORES["."], rect)
                surface.blit(tile_sprites[celda], rect)
            else:
                color = COLORES.get(celda, (0, 0, 0))
                pygame.draw.rect(surface, color, rect)

obstaculos = generar_mapa(mapa)

sprites = {
    "down": [
        cargar_sprites("sprites/Layer 1_sprite_Chef101.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef101.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef102.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef103.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef104.png"),
    ],
    "up": [
        cargar_sprites("sprites/Layer 1_sprite_Chef105.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef105.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef106.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef107.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef108.png"),
    ],
    "right": [
        cargar_sprites("sprites/Layer 1_sprite_Chef109.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef110.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef111.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef112.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef113.png"),
    ],
    "left": [
        cargar_sprites("sprites/Layer 1_sprite_Chef114.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef115.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef116.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef117.png"),
        cargar_sprites("sprites/Layer 1_sprite_Chef118.png"),
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
        
        if dx != 0 or dy != 0:
            self.moving = True
        else:
            self.moving = False

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
        
    def procesar_tiles_especiales(self, mapa, obstaculos):
        global VELOCIDAD

        # celda que ocupa el jugador
        cx = self.hitbox.centerx // TILE_SIZE
        cy = self.hitbox.centery // TILE_SIZE 

        tile_actual = mapa[cy][cx]

        # F velocidad test
        if tile_actual == 'f':
            VELOCIDAD = VELOCIDAD_BASE * 2
        else:
            VELOCIDAD = VELOCIDAD_BASE


        # c colision piso test
        # # deteccion que tiles rodean al playes
        for fila_idx in range(cy - 1, cy + 2):
            for col_idx in range(cx - 1, cx + 2):
                if 0 <= fila_idx < len(mapa) and 0 <= col_idx < len(mapa[0]):
                    if mapa[fila_idx][col_idx] == 'c':
                        tile_rect = pygame.Rect(
                            col_idx * TILE_SIZE,
                            fila_idx * TILE_SIZE,
                            TILE_SIZE, TILE_SIZE
                        )
                        if self.hitbox.colliderect(tile_rect):
                            mapa[fila_idx][col_idx] = '.'
                            obstaculos[:] = generar_mapa(mapa) 
    def interactuar(self, mapa):
        global score_testing
        cx = self.hitbox.centerx // TILE_SIZE
        cy = self.hitbox.centery // TILE_SIZE
        for fila_idx in range(cy - 1, cy + 2):
            for col_idx in range(cx - 1, cx + 2):
                if 0 <= fila_idx < len(mapa) and 0 <= col_idx < len(mapa[0]):
                    if mapa[fila_idx][col_idx] == "e":
                        score_testing += 1
        

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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                player.interactuar(mapa)  # <- nuevo método
    
    player.handle_input(obstaculos)
    player.procesar_tiles_especiales(mapa, obstaculos)
    player.update_animation()

    # 3. Calcular el tiempo restante
    tiempo_actual = pygame.time.get_ticks()
    tiempo_transcurrido = (tiempo_actual - tiempo_inicio) / 1000 # a segundos
    tiempo_restante = max(0, TIEMPO_TOTAL - tiempo_transcurrido)

    # 4. Convertir a formato de minutos y segundos
    minutos = int(tiempo_restante // 60)
    segundos = int(tiempo_restante % 60)
    formato_tiempo = f"{minutos:02}:{segundos:02}"

    pantalla.fill((0,0,0))
    dibujar_mapa(pantalla, mapa)
    # Dibujar el timer
    texto_pantalla = FONT.render(formato_tiempo, False, '#000000')
    pantalla.blit(texto_pantalla, (130, 120))
    texto_score = FONT.render(str(score_testing), False, "#CBDC30")
    pantalla.blit(texto_score, (WIDTH-100, 100))

    player.draw(pantalla)


    pygame.display.flip()
    clock.tick(60)