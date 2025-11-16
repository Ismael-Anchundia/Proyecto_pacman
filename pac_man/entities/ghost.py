# entities/ghost.py
import random
from entities.entity import Entity
from core.renderer import TILE_SIZE
from config import RED

class Ghost(Entity):
    def __init__(self, x, y, level, color=RED, speed=120):
        super().__init__(x, y, speed)
        self.level = level
        self.color = color

        self.directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]

        self.dir_x, self.dir_y = random.choice(self.directions)

    def can_move(self, dx, dy):
        new_x = self.x + dx * TILE_SIZE
        new_y = self.y + dy * TILE_SIZE

        col = int(new_x // TILE_SIZE)
        row = int(new_y // TILE_SIZE)

        if 0 <= row < len(self.level.map) and 0 <= col < len(self.level.map[0]):
            return not self.level.is_wall(col, row)
        return False

    def update(self, dt):
        if not self.can_move(self.dir_x, self.dir_y):
            self.choose_new_direction()
            return

        if self.at_intersection():
            self.choose_new_direction()

        self.x += self.dir_x * self.speed * dt
        self.y += self.dir_y * self.speed * dt

    def at_intersection(self):
        cx = int(self.x) % TILE_SIZE
        cy = int(self.y) % TILE_SIZE
        return cx < 2 and cy < 2

    def choose_new_direction(self):
        valid = [
            (dx, dy)
            for dx, dy in self.directions
            if self.can_move(dx, dy)
            and not (dx == -self.dir_x and dy == -self.dir_y)
        ]
        if valid:
            self.dir_x, self.dir_y = random.choice(valid)

    def draw(self, renderer):
        renderer.draw_circle(int(self.x), int(self.y),
                             TILE_SIZE//2 - 2, self.color)
