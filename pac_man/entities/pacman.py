# entities/pacman.py
import pygame
import math
from entities.entity import Entity
from core.renderer import TILE_SIZE
from config import YELLOW

class Pacman(Entity):
    def __init__(self, x, y, level=None):
        super().__init__(x, y, speed=150)
        self.level = level

        self.dir_x = 0
        self.dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.next_dir_x, self.next_dir_y = -1, 0
        elif keys[pygame.K_RIGHT]:
            self.next_dir_x, self.next_dir_y = 1, 0
        elif keys[pygame.K_UP]:
            self.next_dir_x, self.next_dir_y = 0, -1
        elif keys[pygame.K_DOWN]:
            self.next_dir_x, self.next_dir_y = 0, 1

    def can_move(self, dx, dy):
        new_x = self.x + dx * TILE_SIZE
        new_y = self.y + dy * TILE_SIZE

        col = int(new_x // TILE_SIZE)
        row = int(new_y // TILE_SIZE)

        if 0 <= row < len(self.level.map) and 0 <= col < len(self.level.map[0]):
            return not self.level.is_wall(col, row)
        return False

    def update(self, dt):
        if self.next_dir_x != self.dir_x or self.next_dir_y != self.dir_y:
            if self.can_move(self.next_dir_x, self.next_dir_y):
                self.dir_x = self.next_dir_x
                self.dir_y = self.next_dir_y

        if not self.can_move(self.dir_x, self.dir_y):
            return

        self.x += self.dir_x * self.speed * dt
        self.y += self.dir_y * self.speed * dt

        self.eat_pellets()

    def eat_pellets(self):
        col = int(self.x // TILE_SIZE)
        row = int(self.y // TILE_SIZE)

        if (col, row) in self.level.pellets:
            self.level.pellets.remove((col, row))
            self.level.game.hud.add_score(10)

        if (col, row) in self.level.powerups:
            self.level.powerups.remove((col, row))
            self.level.game.hud.add_score(50)

    def collides_with(self, ghost):
        dist = math.dist((self.x, self.y), (ghost.x, ghost.y))
        return dist < (TILE_SIZE * 0.6)

    def draw(self, renderer):
        renderer.draw_circle(int(self.x), int(self.y),
                             TILE_SIZE // 2 - 2, YELLOW)
