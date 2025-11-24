# core/renderer.py
import pygame

TILE_SIZE = 32  # tamaño en pixeles para cada celda

class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def draw_rect(self, x, y, color):
        pygame.draw.rect(self.screen, color, (x, y, TILE_SIZE, TILE_SIZE))

    def draw_circle(self, x, y, radius, color):
        pygame.draw.circle(self.screen, color, (x, y), radius)

    def draw_text(self, text, x, y, color=(255,255,255), size=24):
        font = pygame.font.SysFont(None, size)
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))
