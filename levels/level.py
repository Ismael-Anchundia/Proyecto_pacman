# levels/level.py
import pygame
from core.renderer import TILE_SIZE
from config import BLUE, WHITE, YELLOW, DARK_BLUE
from levels.level_loader import load_level_file


INNER_BLUE = (80, 80, 255)  # línea interna de neón


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
        
        # ------------------------------
        # Casita (desde JSON)
        # ------------------------------
        self.ghost_house_area = {tuple(p) for p in data.get("ghost_house_area", [])}
        self.ghost_house_door = tuple(data.get("ghost_house_door", ()))


    
    def is_ghost_house(self, col, row):
        tile = self.tiles[row][col]
        return tile in ("-", " ") 




    # ----------------------------------------------------------
    # DIBUJAR MAPA ESTÉTICO (Paredes Neón + Casita)
    # ----------------------------------------------------------
    def draw(self, renderer):
        screen = renderer.screen
        t = TILE_SIZE

        for row_index, row in enumerate(self.tiles):
            for col_index, tile in enumerate(row):

                x = col_index * t
                y = row_index * t

                # ------------------------------------------------------
                # PUERTA (rosada estilo Pac-Man: línea horizontal fina)
                # ------------------------------------------------------
                if tile == "-":
                    door_thickness = 6
                    pygame.draw.rect(
                        screen,
                        (255, 150, 200),
                        (x, y + TILE_SIZE//2 - door_thickness//2, TILE_SIZE, door_thickness)
                    )
                    continue


                # ------------------------------------------------------
                # PAREDES estilo Pac-Man (líneas neón)
                # ------------------------------------------------------
                if tile == "#":
                    pygame.draw.rect(screen, DARK_BLUE, (x, y, t, t))

                    # Helper local
                    def is_wall(c, r):
                        if r < 0 or r >= len(self.tiles):
                            return False
                        if c < 0 or c >= len(self.tiles[0]):
                            return False
                        return self.tiles[r][c] == "#"

                    # Margen de líneas
                    m1 = 2
                    m2 = 5

                    # Arriba
                    if not is_wall(col_index, row_index - 1):
                        pygame.draw.line(screen, BLUE,
                            (x, y + m1), (x + t, y + m1), 2)
                        pygame.draw.line(screen, INNER_BLUE,
                            (x, y + m2), (x + t, y + m2), 2)

                    # Abajo
                    if not is_wall(col_index, row_index + 1):
                        pygame.draw.line(screen, BLUE,
                            (x, y + t - m1 - 1), (x + t, y + t - m1 - 1), 2)
                        pygame.draw.line(screen, INNER_BLUE,
                            (x, y + t - m2 - 1), (x + t, y + t - m2 - 1), 2)

                    # Izquierda
                    if not is_wall(col_index - 1, row_index):
                        pygame.draw.line(screen, BLUE,
                            (x + m1, y), (x + m1, y + t), 2)
                        pygame.draw.line(screen, INNER_BLUE,
                            (x + m2, y), (x + m2, y + t), 2)

                    # Derecha
                    if not is_wall(col_index + 1, row_index):
                        pygame.draw.line(screen, BLUE,
                            (x + t - m1 - 1, y), (x + t - m1 - 1, y + t), 2)
                        pygame.draw.line(screen, INNER_BLUE,
                            (x + t - m2 - 1, y), (x + t - m2 - 1, y + t), 2)

        # ------------------------------------------------------
        # PELLETS
        # ------------------------------------------------------
        for col, row in self.pellets:
            x = col * t + t // 2
            y = row * t + t // 2
            renderer.draw_circle(x, y, 3, WHITE)

        # ------------------------------------------------------
        # POWERUPS
        # ------------------------------------------------------
        for col, row in self.powerups:
            x = col * t + t // 2
            y = row * t + t // 2
            renderer.draw_circle(x, y, 8, YELLOW)

    # ----------------------------------------------------------
    def is_wall(self, col, row):
        if row < 0 or row >= len(self.tiles):
            return True
        if col < 0 or col >= len(self.tiles[row]):
            return True
        return self.tiles[row][col] == "#"

    def is_wall_at_pixel(self, x, y):
        col = x // TILE_SIZE
        row = y // TILE_SIZE
        return self.is_wall(int(col), int(row))
    
    
