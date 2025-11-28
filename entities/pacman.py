# entities/pacman.py
import pygame
import math
from entities.entity import Entity
from core.renderer import TILE_SIZE
from core.sprite_loader import load_folder


# ----------------------------------------------------------
# FUNCIONES PURAS (no modifican estado)
# ----------------------------------------------------------
def direction_vector(dx, dy):
    """Función pura: normaliza dirección."""
    return (dx, dy)


def compute_distance_to_center(x, y, cx, cy):
    """Función pura para cálculo de distancia."""
    return abs(cx - x), abs(cy - y)


# ----------------------------------------------------------
# CLASE PACMAN
# ----------------------------------------------------------
class Pacman(Entity):
    def __init__(self, x, y, level=None):
        super().__init__(x, y, speed=140)
        self.level = level

        # Direcciones
        self.dir_x = 0
        self.dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0
        self.direction = "left"

        # Power-ups
        self.invincible = False
        self.speed_multiplier = 1.0
        self.score_multiplier = 1
        self.effects = []

        # Sprites
        self.anim = {
            "left": load_folder("assets/sprites/pacman/left", TILE_SIZE),
            "right": load_folder("assets/sprites/pacman/right", TILE_SIZE),
            "up": load_folder("assets/sprites/pacman/up", TILE_SIZE),
            "down": load_folder("assets/sprites/pacman/down", TILE_SIZE),
        }

        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 0.10

    # ----------------------------------------------------------
    # HELPERS DE GRID (puras excepto por acceso a estado)
    # ----------------------------------------------------------
    def current_cell(self):
        return int(self.x // TILE_SIZE), int(self.y // TILE_SIZE)

    def tile_center(self, col, row):
        return (
            col * TILE_SIZE + TILE_SIZE / 2,
            row * TILE_SIZE + TILE_SIZE / 2,
        )

    def is_centered(self, tolerance=1.0):
        col, row = self.current_cell()
        cx, cy = self.tile_center(col, row)
        return abs(self.x - cx) <= tolerance and abs(self.y - cy) <= tolerance

    def snap_center_soft(self):
        col, row = self.current_cell()
        cx, cy = self.tile_center(col, row)
        self.x += (cx - self.x) * 0.35
        self.y += (cy - self.y) * 0.35

    # ----------------------------------------------------------
    # INPUT (lambdas)
    # ----------------------------------------------------------
    def handle_input(self, keys):
        direction_map = {
            pygame.K_LEFT:  (-1, 0, "left"),
            pygame.K_RIGHT: (1, 0, "right"),
            pygame.K_UP:    (0, -1, "up"),
            pygame.K_DOWN:  (0, 1, "down"),
        }

        for key, (dx, dy, name) in direction_map.items():
            if keys[key]:
                self.next_dir_x, self.next_dir_y = dx, dy
                self.direction = name

    # ----------------------------------------------------------
    # COLISIONES FUNCIONALES
    # ----------------------------------------------------------
    def can_move(self, dx, dy):
        if dx == 0 and dy == 0:
            return False

        col, row = self.current_cell()
        tcol, trow = col + dx, row + dy

        if trow < 0 or trow >= len(self.level.tiles):
            return False
        if tcol < 0 or tcol >= len(self.level.tiles[0]):
            return False
        # Bloquear casita para Pac-Man
        if self.level.is_ghost_house(tcol, trow):
            return False


        return not self.level.is_wall(tcol, trow)

    # ----------------------------------------------------------
    # UPDATE PRINCIPAL (sin cambios de lógica)
    # ----------------------------------------------------------
    def update(self, dt):

        # Intentar girar si está centrado
        if self.is_centered():
            self.snap_center_soft()

            if self.can_move(self.next_dir_x, self.next_dir_y):
                self.dir_x = self.next_dir_x
                self.dir_y = self.next_dir_y

            if not self.can_move(self.dir_x, self.dir_y):
                self.finish_update(dt)
                return

        move_step = self.speed * self.speed_multiplier * dt

        col, row = self.current_cell()
        cx, cy = self.tile_center(col, row)

        dist_x = cx - self.x
        dist_y = cy - self.y

        limit = abs(dist_x) if self.dir_x != 0 else abs(dist_y)

        if move_step > limit and limit > 0.1:
            # No pasar centro
            self.x += self.dir_x * limit
            self.y += self.dir_y * limit

            self.snap_center_soft()

            if self.can_move(self.dir_x, self.dir_y):
                leftover = move_step - limit
                self.x += self.dir_x * leftover
                self.y += self.dir_y * leftover

            self.finish_update(dt)
            return

        # Movimiento normal
        self.x += self.dir_x * move_step
        self.y += self.dir_y * move_step

        if self.is_centered():
            self.snap_center_soft()

        self.finish_update(dt)

    # ----------------------------------------------------------
    # FINAL UPDATE
    # ----------------------------------------------------------
    def finish_update(self, dt):
        # Sprite
        frames = self.anim.get(self.direction, [])
        if frames:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % len(frames)

        # Items
        self.eat_items()

        # Power-ups
        self.update_effects(dt)

    # ----------------------------------------------------------
    # ITEMS / POWERUPS
    # ----------------------------------------------------------
    def eat_items(self):
        col, row = self.current_cell()

        if (col, row) in self.level.pellets:
            self.level.pellets.remove((col, row))
            self.level.game.hud.add_score(10 * self.score_multiplier)

        if (col, row) in self.level.powerups:
            self.level.powerups.remove((col, row))
            self.level.game.activate_powerup(self, col, row)

    # ----------------------------------------------------------
    # EFECTOS (PATRÓN DE CLOSURES)
    # ----------------------------------------------------------
    def add_effect(self, effect):
        effect.remaining_time = getattr(effect, "duration", 0)
        effect.apply(self)
        self.effects.append(effect)

    def update_effects(self, dt):
        expired = []

        for e in self.effects:
            e.remaining_time -= dt
            if e.remaining_time <= 0:
                expired.append(e)

        for e in expired:
            e.remove(self)
            self.effects.remove(e)

    # ----------------------------------------------------------
    # COLISIONES PACMAN/GHOST
    # ----------------------------------------------------------
    def collides_with(self, ghost):
        return math.dist((self.x, self.y), (ghost.x, ghost.y)) < (TILE_SIZE * 0.6)

    # ----------------------------------------------------------
    # DRAW
    # ----------------------------------------------------------
    def draw(self, renderer):
        frames = self.anim.get(self.direction, [])
        if frames:
            frame = frames[self.anim_frame % len(frames)]
            renderer.screen.blit(
                frame,
                (self.x - TILE_SIZE // 2, self.y - TILE_SIZE // 2)
            )
