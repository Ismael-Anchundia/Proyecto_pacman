# entities/pacman.py
import pygame
from entities.entity import Entity
from core.renderer import TILE_SIZE
from config import YELLOW

class Pacman(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, speed=150)

    def handle_input(self, keys):
        self.dir_x = 0
        self.dir_y = 0

        if keys[pygame.K_LEFT]:
            self.dir_x = -1
        elif keys[pygame.K_RIGHT]:
            self.dir_x = 1

        if keys[pygame.K_UP]:
            self.dir_y = -1
        elif keys[pygame.K_DOWN]:
            self.dir_y = 1

    def draw(self, renderer):
        renderer.draw_circle(
            int(self.x),
            int(self.y),
            TILE_SIZE // 2 - 2,
            YELLOW
        )
