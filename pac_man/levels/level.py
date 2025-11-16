# levels/level.py
from core.renderer import TILE_SIZE
from config import BLUE, WHITE, YELLOW

class Level:
    def __init__(self, map_file, game=None):
        self.game = game
        self.map = []
        self.pellets = []
        self.powerups = []
        self.ghost_spawns = []

        self.pacman_spawn = (12, 8)

        self.load_map(map_file)

    def load_map(self, file):
        with open(file, "r") as f:
            for row_index, line in enumerate(f):
                line = line.rstrip("\n")
                self.map.append(line)

                for col_index, char in enumerate(line):
                    if char == ".":
                        self.pellets.append((col_index, row_index))
                    elif char == "o":
                        self.powerups.append((col_index, row_index))
                    elif char == "G":
                        self.ghost_spawns.append((col_index, row_index))

    def draw(self, renderer):
        for row_index, row in enumerate(self.map):
            for col_index, tile in enumerate(row):
                if tile == "#":
                    renderer.draw_rect(col_index * TILE_SIZE, row_index * TILE_SIZE, BLUE)

        for col, row in self.pellets:
            renderer.draw_circle(col * TILE_SIZE + TILE_SIZE//2,
                                 row * TILE_SIZE + TILE_SIZE//2,
                                 3, WHITE)

        for col, row in self.powerups:
            renderer.draw_circle(col * TILE_SIZE + TILE_SIZE//2,
                                 row * TILE_SIZE + TILE_SIZE//2,
                                 8, YELLOW)

    def is_wall(self, col, row):
        return self.map[row][col] == "#"

    def is_wall_at_pixel(self, x, y):
        col = x // TILE_SIZE
        row = y // TILE_SIZE
        return self.is_wall(col, row)
