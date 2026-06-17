import pygame
from configuracion import *

MENSAJES_FINALES = [
    (3000, "LEYENDA ABSOLUTA, CRACK, AURA, NAHH GENIO GENIO"),
    (2000, "Excelentee bro, muy bien todo."),
    (1000, "Nada mal! Aunque algunos platos quedaron en el camino..."),
    (500,  "Sobreviviste los tres niveles... apenas."),
    (0,    "nah.. retirate mejor"),
]

class PantallaFinalEscena:
    def __init__(self, puntos_nivel1, puntos_nivel2, puntos_nivel3):
        self.siguiente_estado = None

        self.puntos_nivel1 = puntos_nivel1
        self.puntos_nivel2 = puntos_nivel2
        self.puntos_nivel3 = puntos_nivel3
        self.puntos_total  = puntos_nivel1 + puntos_nivel2 + puntos_nivel3

        # fade in al entrar
        self.fade_alpha = 255
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surface.fill('#000000')

        # elegir mensaje segun puntos totales
        self.mensaje = MENSAJES_FINALES[-1][1]
        for minimo, texto in MENSAJES_FINALES:
            if self.puntos_total >= minimo:
                self.mensaje = texto
                break

    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self.siguiente_estado = 'Menu'

    def actualizar(self):
        # fade in al entrar
        if self.fade_alpha > 0:
            self.fade_alpha -= VELOCIDAD_FADE
            self.fade_alpha = max(0, self.fade_alpha)

    def dibujar(self, pantalla, font_grande, font_mediana, font_pequena):
        pantalla.fill('#0a0a0a')

        # titulo
        texto_titulo = font_grande.render('JUEGO COMPLETADO', False, '#ffd700')
        pantalla.blit(texto_titulo, (WIDTH // 2 - texto_titulo.get_width() // 2, 60))

        # linea separadora
        pygame.draw.rect(pantalla, '#333333', (80, 110, WIDTH - 160, 2))

        # resumen por nivel
        y_base = 140

        # nivel 1
        texto_n1 = font_mediana.render('La Cali', False, '#aaaaff')
        texto_p1 = font_mediana.render(f'{self.puntos_nivel1} pts', False, '#ffffff')
        pantalla.blit(texto_n1, (120, y_base))
        pantalla.blit(texto_p1, (WIDTH - 200, y_base))

        # nivel 2
        texto_n2 = font_mediana.render('Pizzeria Turing', False, '#ffaa55')
        texto_p2 = font_mediana.render(f'{self.puntos_nivel2} pts', False, '#ffffff')
        pantalla.blit(texto_n2, (120, y_base + 50))
        pantalla.blit(texto_p2, (WIDTH - 200, y_base + 50))

        # nivel 3
        texto_n3 = font_mediana.render('La Casita Forestal', False, '#55cc88')
        texto_p3 = font_mediana.render(f'{self.puntos_nivel3} pts', False, '#ffffff')
        pantalla.blit(texto_n3, (120, y_base + 100))
        pantalla.blit(texto_p3, (WIDTH - 200, y_base + 100))

        # linea separadora total
        pygame.draw.rect(pantalla, '#555555', (80, y_base + 140, WIDTH - 160, 2))

        # total
        texto_total_label = font_grande.render('TOTAL', False, '#ffffff')
        texto_total_pts   = font_grande.render(f'{self.puntos_total} pts', False, '#ffd700')
        pantalla.blit(texto_total_label, (120, y_base + 160))
        pantalla.blit(texto_total_pts,   (WIDTH - 200, y_base + 160))

        # barra visual del total — relativa al maximo posible
        maximo_posible = 4000
        progreso = min(1, self.puntos_total / maximo_posible)
        ancho_barra = int((WIDTH - 160) * progreso)
        pygame.draw.rect(pantalla, '#333333', (80, y_base + 220, WIDTH - 160, 12), border_radius=6)
        pygame.draw.rect(pantalla, '#ffd700', (80, y_base + 220, ancho_barra, 12), border_radius=6)

        # mensaje personalizado
        texto_msg = font_mediana.render(self.mensaje, False, '#aaaacc')
        pantalla.blit(texto_msg, (WIDTH // 2 - texto_msg.get_width() // 2, y_base + 260))

        # instruccion escape
        texto_esc = font_pequena.render('Presiona ESC para volver al menu', False, '#666666')
        pantalla.blit(texto_esc, (WIDTH // 2 - texto_esc.get_width() // 2, HEIGHT - 40))

        # fade in encima
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(self.fade_alpha)
            pantalla.blit(self.fade_surface, (0, 0))