import pygame
from configuracion import *


class MenuEscena:
    def __init__(self):
        self.siguiente_estado = None # no quiero cambiar de escena
        self.fondo = pygame.image.load('sprites/fondo_menu.png').convert()
        self.visible = True
        self.timer = 0

        # musica
        pygame.mixer.music.load("sonidos/menu_music.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        

    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                pygame.mixer.music.stop() # parar musica
                self.siguiente_estado = 'Jugando' # cambiar estado

    def actualizar(self):
        # Efecto parpadeo
        self.timer += 1
        if self.timer >= 15: # cada n frames
            self.visible = not self.visible
            self.timer = 0


    def dibujar(self, pantalla, font_grande, font_mediana, font_pequena):
        pantalla.blit(self.fondo, (0,0))
        pygame.draw.rect(pantalla, '#000000',(80, 440,600,60))
        texto = font_grande.render("Presiona ENTER para jugar", False, "#ffffff")
        if self.visible:
            pantalla.blit(texto, (100, 450))
