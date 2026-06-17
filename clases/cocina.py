import pygame
import random
from configuracion import *
from clases.receta import Receta

class Cocina:
    def __init__(self, chefs, shakers, licuadoras, barras, recetas_posibles, tiempo_total):
        self.chefs = chefs
        self.shakers = shakers # nivel1=shakers,  nivel2=hornos
        self.licuadoras = licuadoras # nivel1=licuadoras, nivel2=mesas
        self.barras = barras
        self.recetas_posibles = recetas_posibles

        self.ordenes = []
        self.max_ordenes = MAX_ORDENES

        self.puntos = 0
        self.tiempo_total = tiempo_total * 60 # a (60 fps)
        self.tiempo_restante = tiempo_total * 60

        #generador de recetas
        self.timer_receta = 0
        self.intervalo_receta = random.randint(INTERVALO_RECETA_MIN,INTERVALO_RECETA_MAX) * 60
        self.primer_receta_timer = PRIMERA_RECETA_DELAY * 60 # primera receta a als 5s
        self.primer_receta_generada = False


    def actualizar(self, obstaculos):
        # actualizar cheffs
        for chef in self.chefs:
            chef.manejar_inputs(obstaculos, VELOCIDAD_CHEF)
            chef.actualizar_animacion()

        # actualizar estaciones
        for shaker in self.shakers:
            shaker.actualizar(self.recetas_posibles)
        for licuadora in self.licuadoras:
            licuadora.actualizar()

        # actualizar timer
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1

        # actualizar recetas act
        self._actualizar_ordenes()

        # generar recetas
        self._generar_receta_con_timer()
    
    # TIMER DE RECETAS
    def _generar_receta_con_timer(self):
        # primera receta
        if not self.primer_receta_generada:
            self.primer_receta_timer -= 1
            if self.primer_receta_timer <= 0:
                self.generar_receta()
                self.primer_receta_generada = True
            return

        # siguientes recetas
        self.timer_receta += 1
        if self.timer_receta >= self.intervalo_receta:
            self.generar_receta()
            self.timer_receta = 0
            self.intervalo_receta = random.randint(INTERVALO_RECETA_MIN, INTERVALO_RECETA_MAX) * 60

    def generar_receta(self):
        if len(self.ordenes) < self.max_ordenes:
            receta = random.choice(self.recetas_posibles)
            # crea un copia para no reutilizar mismo objeto
            nueva = Receta(receta.nombre, receta.ingredientes)
            self.ordenes.append(nueva)

    # ACTUALIZAR ORDENES ACTIVAS
    def _actualizar_ordenes(self):
        for receta in self.ordenes[:]: # itera sobre copia
            receta.tiempo_actual += 1

            # cuando llega al tiempo max, reduce puntos a la mitad
            if receta.tiempo_actual >= receta.tiempo_max * 60:
                # resta puntos actuales al jugador
                self.puntos = max(0, self.puntos - receta.puntos)

                receta.puntos = receta.puntos // 2
                receta.tiempo_actual = 0  # reset timer para volver a contar
                receta.veces_expirada += 1

                # si se repite ya 3 veces se elimina la receta
                if receta.veces_expirada >= MAX_EXPIRACIONES:
                    self.ordenes.remove(receta)
    
    # Puntuacion
    def agregar_puntos(self, cantidad):
        self.puntos += cantidad

    def entregar_receta(self, chef):
        if chef.en_mano is None:
            return
        if not isinstance(chef.en_mano, Receta):
            chef.en_mano = None
            return
        for receta in self.ordenes:
            if chef.en_mano.nombre == receta.nombre:
                self.agregar_puntos(receta.puntos)
                self.ordenes.remove(receta)
                chef.en_mano = None
                return
        # No coincide con ninguna orden
        chef.en_mano = None


    # = HUD =
    def dibujar_hud(self, pantalla, font_grande, font_mediana, font_pequena, nombre_nivel):
        #fondo
        pygame.draw.rect(pantalla, '#1a1a2e', (0,0, WIDTH, TILE_SIZE))
        pygame.draw.rect(pantalla, "#1a1a2e", (48*16,48, 48*6, 48*11))

        # tARJETAS DE RECETAS
        ancho_tarjeta = TILE_SIZE * 5 - 12
        alto_tarjeta = TILE_SIZE * 3
        margen_x = 6 + 768
        margen_y = TILE_SIZE * 2 + 12

        # recetas activas
        for i, receta in enumerate(self.ordenes):
            x = margen_x
            y = margen_y + i * (alto_tarjeta + (margen_y - TILE_SIZE) - 48)
            
            # fondo tarjeta
            pygame.draw.rect(pantalla, '#2e2e4e', (x, y, ancho_tarjeta, alto_tarjeta), border_radius=6)
            pygame.draw.rect(pantalla, '#5555aa', (x, y, ancho_tarjeta, alto_tarjeta), 2, border_radius=6)

            # sprite de la receta
            pantalla.blit(receta.sprite, (x + (ancho_tarjeta / 2) - (receta.sprite.get_width()// 2), y + 24))

            # nombre receta
            texto_nombre = font_mediana.render(receta.nombre, False, '#ffffff')
            pantalla.blit(texto_nombre, (x + 4, y + 4 ))

            # ingredientes
            for j, ing in enumerate(receta.ingredientes):
                texto_ing = font_pequena.render(f'• {ing}', False, '#aaaacc')
                if j >= 3:
                    pantalla.blit(texto_ing, (x + 4 + (ancho_tarjeta // 2), y + 62 + (j - 3) * 14))
                else:
                    pantalla.blit(texto_ing, (x + 4, y + 62 + j * 14))

            # puntos
            texto_pts = font_pequena.render(f'{receta.puntos}pts', False, '#ffd700')
            pantalla.blit(texto_pts, (x + 4, y + alto_tarjeta - 30))

            # barra de tiempo restante
            progreso = 1 - (receta.tiempo_actual / (receta.tiempo_max * 60))
            progreso = max(0, min(1, progreso)) # entre 0 y 1

            # color de la barra segun urgencia
            if progreso > 0.5:
                color_barra = '#44cc44'
            elif progreso > 0.25:
                color_barra = '#ffaa00'
            else:
                color_barra = '#cc2222'

            ancho_barra = int((ancho_tarjeta - 8) * progreso)
            pygame.draw.rect(pantalla, '#333355', (x + 4, y + alto_tarjeta - 14, ancho_tarjeta - 8, 8), border_radius=3)
            pygame.draw.rect(pantalla, color_barra, (x + 4, y + alto_tarjeta - 14, ancho_barra, 8), border_radius=3)

        # nombre nivel
        texto_nivel = font_grande.render(nombre_nivel, False, '#ffffff')
        pantalla.blit(texto_nivel, (8, 8)) #(WIDTH // 2) - (texto_nivel.get_width() // 2)

        # texto recetas 
        texto_recetas = font_grande.render('RECETAS', False, '#ffffff')
        pantalla.blit(texto_recetas, (TILE_SIZE * 17 + (TILE_SIZE//2) - 24 ,8 + TILE_SIZE))

        # tiempo
        minutos = self.tiempo_restante // 60 // 60
        segundos = self.tiempo_restante // 60 % 60
        if self.tiempo_restante > 30 * 60:
            color_tiempo = '#ffffff'
        else:
            color_tiempo = '#ff4444'
        texto_tiempo = font_grande.render(f'{minutos:02}:{segundos:02}', False, color_tiempo)
        pantalla.blit(texto_tiempo, ((WIDTH // 2) - (texto_nivel.get_width() // 2), 8))

        # puntos
        texto_pts = 'Puntos: ' + str(self.puntos)
        texto_puntos = font_grande.render(texto_pts, False, '#ffd700')
        pantalla.blit(texto_puntos, (WIDTH - 200, 8))

    def dibujar(self, pantalla):
        for chef in self.chefs:
            chef.dibujar(pantalla)
        for shaker in self.shakers:
            shaker.dibujar(pantalla)
        for licuadora in self.licuadoras:
            licuadora.dibujar(pantalla)
        for barra in self.barras:
            barra.dibujar(pantalla)

        
