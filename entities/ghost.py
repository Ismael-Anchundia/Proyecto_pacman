import random
import os
from entities.entity import Entity
from core.renderer import TILE_SIZE
from core.sprite_loader import load_folder


class Ghost(Entity):
    def __init__(self, x, y, level, color="red", speed=90):
        super().__init__(x, y, speed)
        self.level = level
        self.color = color
        self.frozen = False

        base = f"assets/sprites/ghosts/{color}"

        self.anim = {
            "left": self.load_safe(base + "/left"),
            "right": self.load_safe(base + "/right"),
            "up": self.load_safe(base + "/up"),
            "down": self.load_safe(base + "/down")
        }

        if all(len(frames) == 0 for frames in self.anim.values()):
            frames = self.load_safe(base)
            self.anim = {d: frames for d in ["left","right","up","down"]}

        self.direction = "left"
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 0.15

        self.dir_x, self.dir_y = random.choice([(1,0),(-1,0),(0,1),(0,-1)])


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

    def is_centered(self, tolerance=1.5):
        col, row = self.current_cell()
        cx, cy = self.tile_center(col, row)
        return abs(self.x - cx) <= tolerance and abs(self.y - cy) <= tolerance

    def snap_center_soft(self):
        col, row = self.current_cell()
        cx, cy = self.tile_center(col, row)
        self.x += (cx - self.x) * 0.35
        self.y += (cy - self.y) * 0.35


    # ----------------------------------------------------------
    # SPRITE LOADER
    # ----------------------------------------------------------
    def load_safe(self, folder):
        if not os.path.exists(folder):
            return []
        return load_folder(folder, TILE_SIZE)


    # ----------------------------------------------------------
    # TILE COLLISION
    # ----------------------------------------------------------
    def can_move(self, dx, dy):
        col, row = self.current_cell()
        tcol = col + dx
        trow = row + dy

        if trow < 0 or trow >= len(self.level.tiles):
            return False
        if tcol < 0 or tcol >= len(self.level.tiles[0]):
            return False

        return not self.level.is_wall(tcol, trow)


    # ----------------------------------------------------------
    # DECISION DE DIRECCIÓN
    # ----------------------------------------------------------
    def choose_new_direction(self):
        options = []

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:

            # evitar reversa estricta
            if dx == -self.dir_x and dy == -self.dir_y:
                continue

            if self.can_move(dx, dy):
                options.append((dx, dy))

        if not options:
            # si no hay opciones → permitir reversa
            if self.can_move(-self.dir_x, -self.dir_y):
                self.dir_x *= -1
                self.dir_y *= -1
            return

        self.dir_x, self.dir_y = random.choice(options)


    # ----------------------------------------------------------
    # UPDATE — Movimiento suave
    # ----------------------------------------------------------
    def update(self, dt):
        if self.frozen:
            return

        # 1. Si está centrado → decidir nueva dirección
        if self.is_centered():
            self.snap_center_soft()
            self.choose_new_direction()

            # si de casualidad la dirección elegida choca, no moverse
            if not self.can_move(self.dir_x, self.dir_y):
                return

        # 2. Movimiento
        step = self.speed * dt
        self.x += self.dir_x * step
        self.y += self.dir_y * step

        # 3. Snap suave al centro
        if self.is_centered():
            self.snap_center_soft()

        # 4. Actualizar orientación del sprite
        if self.dir_x < 0:
            self.direction = "left"
        elif self.dir_x > 0:
            self.direction = "right"
        elif self.dir_y < 0:
            self.direction = "up"
        elif self.dir_y > 0:
            self.direction = "down"

        # 5. Animación
        frames = self.anim[self.direction]
        if len(frames) > 1:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % len(frames)


    # ----------------------------------------------------------
    # DRAW
    # ----------------------------------------------------------
    def draw(self, renderer):
        frames = self.anim[self.direction]
        if not frames:
            return

        frame = frames[self.anim_frame % len(frames)]
        renderer.screen.blit(
            frame,
            (self.x - TILE_SIZE // 2, self.y - TILE_SIZE // 2)
        )
