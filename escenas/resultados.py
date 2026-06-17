import pygame
from configuracion import *

# Cambiar los mensajes obvio
MENSAJES = [
    (1300, "NAHH fenomeno, idolo, crack, aura, balon de oro"),
    (800, "Muy bien, La Cali te necesita mas"),
    (200, "No estuvo mal... pero meh"),
    (0,   "Mejor ni picha JAJA "),
]

class ResultadosEscena:
    def __init__(self, puntos, siguiente_nivel):
        self.siguiente_estado = None
        self.puntos = puntos
        self.siguiente_nivel = siguiente_nivel
        self.timer = 0
        self.duracion = DURACION_PANTALLA_R * 60 # 5s frames

        # fade in al entrar
        self.fade_alpha = 255 
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surface.fill('#000000')

        # elegir mensaje según puntos
        self.mensaje = MENSAJES[-1][1]
        for minimo, texto in MENSAJES:
            if self.puntos >= minimo:
                self.mensaje = texto
                break

    def manejar_eventos(self, eveto):
        pass

    def actualizar(self):
        self.timer += 1 

        # fade in al entrar
        if self.fade_alpha > 0:
            self.fade_alpha -= VELOCIDAD_FADE
            self.fade_alpha = max(0, self.fade_alpha)

        # dsp 5s pasar lvl2
        if self.timer >= self.duracion:
            self.siguiente_estado = self.siguiente_nivel
    
    def dibujar(self, pantalla,font_grande, font_mediana, font_pequena):
        pantalla.fill('#000000')

        #title
        texto_titulo = font_grande.render('Nivel Completado', False, '#ffffff')
        pantalla.blit(texto_titulo, (WIDTH // 2 - texto_titulo.get_width() // 2, 180))

        # puntos
        texto_puntos = font_grande.render(f'Puntos: {self.puntos}', False, '#ffd700')
        pantalla.blit(texto_puntos, (WIDTH // 2 - texto_puntos.get_width() // 2, 260))

        # mensaje
        texto_msg = font_mediana.render(self.mensaje, False, '#aaaacc')
        pantalla.blit(texto_msg, (WIDTH // 2 - texto_msg.get_width() // 2, 340))

        # contador visual de cuánto falta
        progreso = self.timer / self.duracion
        ancho_barra = int((WIDTH - 100) * progreso)
        pygame.draw.rect(pantalla, '#333333', (50, 420, WIDTH - 100, 8), border_radius=4)
        pygame.draw.rect(pantalla, '#5555aa', (50, 420, ancho_barra, 8), border_radius=4)

        # fade in encima
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(self.fade_alpha)
            pantalla.blit(self.fade_surface, (0, 0))