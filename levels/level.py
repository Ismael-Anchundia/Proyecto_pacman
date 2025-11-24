# levels/level.py
import pygame
from core.renderer import TILE_SIZE
from config import BLUE, WHITE, YELLOW
from levels.level_loader import load_level_file

class Level:
    def __init__(self, map_file, game):
        self.game = game
        self.map_file = map_file

        data = load_level_file(map_file)

        self.tiles = data["tiles"]
        self.pacman_spawn = tuple(data["pacman_spawn"])
        self.ghost_spawns = [tuple(pos) for pos in data["ghost_spawns"]]

        self.pellets = [tuple(p) for p in data["pellets"]]
        self.powerups = [tuple(p) for p in data["powerups"]]

    def draw(self, renderer):
        # Dibujar paredes
        for row_index, row in enumerate(self.tiles):
            for col_index, tile in enumerate(row):
                if tile == "#":
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    renderer.draw_rect(x, y, BLUE)

        # (Opcional) DEBUG de colisiones reales
        # for row in range(len(self.tiles)):
        #     for col in range(len(self.tiles[row])):
        #         if self.is_wall(col, row):
        #             pygame.draw.rect(
        #                 renderer.screen,
        #                 (255, 0, 0),
        #                 (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE),
        #                 1
        #             )

        # Pellets
        for col, row in self.pellets:
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = row * TILE_SIZE + TILE_SIZE // 2
            renderer.draw_circle(x, y, 3, WHITE)

        # Powerups
        for col, row in self.powerups:
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = row * TILE_SIZE + TILE_SIZE // 2
            renderer.draw_circle(x, y, 8, YELLOW)

    def is_wall(self, col, row):
        # Blindaje total contra índices fuera de rango
        if row < 0 or row >= len(self.tiles):
            return True
        if col < 0 or col >= len(self.tiles[row]):
            return True
        return self.tiles[row][col] == "#"

    def is_wall_at_pixel(self, x, y):
        col = x // TILE_SIZE
        row = y // TILE_SIZE
        return self.is_wall(int(col), int(row))
