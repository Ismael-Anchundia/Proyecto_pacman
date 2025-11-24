# entities/ghost.py
import random
import os
from entities.entity import Entity
from core.renderer import TILE_SIZE
from core.sprite_loader import load_folder


class Ghost(Entity):
    def __init__(self, x, y, level, color="red", speed=100):
        # Usamos el mismo sistema: x, y = centro
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

        # Si no hay animaciones por dirección, usar carpeta base
        if all(len(frames) == 0 for frames in self.anim.values()):
            frames = self.load_safe(base)
            self.anim = {
                "left": frames,
                "right": frames,
                "up": frames,
                "down": frames
            }

        self.direction = "left"
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 0.15

        # Direcciones posibles: izquierda, derecha, arriba, abajo
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.dir_x, self.dir_y = random.choice(self.directions)

    # ----------------------------------------------------------
    # Ayudas de grilla
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

    def snap_to_center(self):
        col, row = self.current_cell()
        cx, cy = self.tile_center(col, row)
        self.x = cx
        self.y = cy

    # ----------------------------------------------------------
    def load_safe(self, folder):
        if not os.path.exists(folder):
            return []
        return load_folder(folder, TILE_SIZE)

    # ----------------------------------------------------------
    def can_move(self, dx, dy):
        if dx == 0 and dy == 0:
            return False

        col, row = self.current_cell()
        target_col = col + dx
        target_row = row + dy

        if target_row < 0 or target_row >= len(self.level.tiles):
            return False
        if target_col < 0 or target_col >= len(self.level.tiles[0]):
            return False

        return not self.level.is_wall(target_col, target_row)

    # ----------------------------------------------------------
    def choose_new_direction(self):
        """
        Elige una nueva dirección válida, evitando girar 180° directo.
        """
        valid = []
        for dx, dy in self.directions:
            # evitar rumbo inverso
            if dx == -self.dir_x and dy == -self.dir_y:
                continue
            if self.can_move(dx, dy):
                valid.append((dx, dy))

        if valid:
            self.dir_x, self.dir_y = random.choice(valid)

    # ----------------------------------------------------------
    def update(self, dt):
        if self.frozen:
            return

        # 1) Si está centrado, ajustar al centro exacto y decidir dirección
        if self.is_centered():
            self.snap_to_center()

            # Si delante hay muro, forzar nueva dirección
            if not self.can_move(self.dir_x, self.dir_y):
                self.choose_new_direction()
            else:
                # A veces cambiar de dirección en intersecciones
                if random.random() < 0.20:
                    self.choose_new_direction()

        # 2) Mover solo si la dirección actual es válida
        if self.can_move(self.dir_x, self.dir_y):
            self.x += self.dir_x * self.speed * dt
            self.y += self.dir_y * self.speed * dt
        else:
            # Estamos contra una pared: intentar elegir otra dirección
            self.choose_new_direction()

        # 3) Actualizar dirección para sprites
        if self.dir_x < 0:
            self.direction = "left"
        elif self.dir_x > 0:
            self.direction = "right"
        elif self.dir_y < 0:
            self.direction = "up"
        elif self.dir_y > 0:
            self.direction = "down"

        # 4) Animación
        frames = self.anim[self.direction]
        if len(frames) > 1:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % len(frames)

    # ----------------------------------------------------------
    def draw(self, renderer):
        frames = self.anim[self.direction]
        if len(frames) == 0:
            # fallback por si faltan sprites
            for dir_frames in self.anim.values():
                if len(dir_frames) > 0:
                    frames = dir_frames
                    break
        if len(frames) == 0:
            return

        frame = frames[self.anim_frame % len(frames)]
        # x, y son centro
        renderer.screen.blit(frame, (self.x - TILE_SIZE // 2, self.y - TILE_SIZE // 2))
