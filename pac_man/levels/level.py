# levels/level.py
from core.renderer import TILE_SIZE
from config import BLUE, WHITE

class Level:
    def __init__(self, map_file):
        self.map = []
        self.load_map(map_file)

    def load_map(self, file):
        with open(file, "r") as f:
            for line in f:
                self.map.append(line.rstrip("\n"))

    def draw(self, renderer):
        for row_index, row in enumerate(self.map):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if tile == "#":
                    renderer.draw_rect(x, y, BLUE)
                elif tile == ".":
                    renderer.draw_rect(x, y, WHITE)
