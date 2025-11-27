import pygame
import math
from entities.entity import Entity
from core.renderer import TILE_SIZE
from core.sprite_loader import load_folder


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
    # GRID HELPERS
    # ----------------------------------------------------------
    def current_cell(self):
        col = int(self.x // TILE_SIZE)
        row = int(self.y // TILE_SIZE)
        return col, row

    def tile_center(self, col, row):
        cx = col * TILE_SIZE + TILE_SIZE / 2
        cy = row * TILE_SIZE + TILE_SIZE / 2
        return cx, cy

    def is_centered(self, tolerance=1.0):
        col, row = self.current_cell()
        cx, cy = self.tile_center(col, row)
        return abs(self.x - cx) <= tolerance and abs(self.y - cy) <= tolerance

    def snap_center_soft(self):
        """Snap suave para evitar tirones."""
        col, row = self.current_cell()
        cx, cy = self.tile_center(col, row)
        self.x += (cx - self.x) * 0.35
        self.y += (cy - self.y) * 0.35


    # ----------------------------------------------------------
    # INPUT
    # ----------------------------------------------------------
    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.next_dir_x, self.next_dir_y = -1, 0
            self.direction = "left"
        elif keys[pygame.K_RIGHT]:
            self.next_dir_x, self.next_dir_y = 1, 0
            self.direction = "right"
        elif keys[pygame.K_UP]:
            self.next_dir_x, self.next_dir_y = 0, -1
            self.direction = "up"
        elif keys[pygame.K_DOWN]:
            self.next_dir_x, self.next_dir_y = 0, 1
            self.direction = "down"


    # ----------------------------------------------------------
    # TILE COLLISION
    # ----------------------------------------------------------
    def can_move(self, dx, dy):
        if dx == 0 and dy == 0:
            return False

        col, row = self.current_cell()
        tcol = col + dx
        trow = row + dy

        if trow < 0 or trow >= len(self.level.tiles):
            return False
        if tcol < 0 or tcol >= len(self.level.tiles[0]):
            return False

        return not self.level.is_wall(tcol, trow)


    # ----------------------------------------------------------
    # UPDATE — Movimiento arcade suave
    # ----------------------------------------------------------
    def update(self, dt):

        # 1. Intentar girar si estamos centrados
        if self.is_centered():
            self.snap_center_soft()

            if self.can_move(self.next_dir_x, self.next_dir_y):
                self.dir_x = self.next_dir_x
                self.dir_y = self.next_dir_y

            if not self.can_move(self.dir_x, self.dir_y):
                self.finish_update(dt)
                return

        # Movimiento del frame
        move_step = self.speed * self.speed_multiplier * dt

        col, row = self.current_cell()
        cx, cy = self.tile_center(col, row)

        dist_x = cx - self.x
        dist_y = cy - self.y

        if self.dir_x != 0:
            limit = abs(dist_x)
        else:
            limit = abs(dist_y)

        # No pasar del centro del tile
        if move_step > limit and limit > 0.1:
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
    # FINAL UPDATE STAGE
    # ----------------------------------------------------------
    def finish_update(self, dt):
        # Animación
        frames = self.anim.get(self.direction, [])
        if frames:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % len(frames)

        # Pellets
        self.eat_items()

        # Powerups
        self.update_effects(dt)


    # ----------------------------------------------------------
    # ITEMS
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
    # EFFECTS SYSTEM
    # ----------------------------------------------------------
    def add_effect(self, effect):
        """Agrega un efecto tipo powerup."""
        effect.remaining_time = getattr(effect, "duration", 0)
        effect.apply(self)
        self.effects.append(effect)

    def update_effects(self, dt):
        to_remove = []
        for e in self.effects:
            e.remaining_time -= dt
            if e.remaining_time <= 0:
                e.remove(self)
                to_remove.append(e)

        for e in to_remove:
            if e in self.effects:
                self.effects.remove(e)


    # ----------------------------------------------------------
    # COLLISION WITH GHOST
    # ----------------------------------------------------------
    def collides_with(self, ghost):
        dist = math.dist((self.x, self.y), (ghost.x, ghost.y))
        return dist < (TILE_SIZE * 0.6)


    # ----------------------------------------------------------
    # DRAW
    # ----------------------------------------------------------
    def draw(self, renderer):
        frames = self.anim.get(self.direction, [])
        if not frames:
            return

        frame = frames[self.anim_frame % len(frames)]
        renderer.screen.blit(
            frame,
            (self.x - TILE_SIZE // 2, self.y - TILE_SIZE // 2)
        )
