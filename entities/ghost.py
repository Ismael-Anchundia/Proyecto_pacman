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

        # ESTADOS DEL FANTASMA
        self.state = "normal"     # normal, fright, blink, eyes
        self.fright_timer = 0
        self.fright_duration = 6
        self.blink_threshold = 2

        # Velocidades por estado
        self.base_speed = speed          # 90
        self.fright_speed = 65           # fijo, no multiplicar
        self.eyes_speed = 160            # rápido hacia el spawn

        # Posición del respawn
        self.spawn_x = x
        self.spawn_y = y

        # --------------------------
        # SPRITES NORMALES
        # --------------------------
        base = f"assets/sprites/ghosts/{color}"

        self.anim_normal = {
            "left":  self.load_safe(base + "/left"),
            "right": self.load_safe(base + "/right"),
            "up":    self.load_safe(base + "/up"),
            "down":  self.load_safe(base + "/down"),
        }

        # FRIGHT (AZUL)
        self.anim_fright = {
            "left":  self.load_safe("assets/sprites/ghosts/fright"),
            "right": self.load_safe("assets/sprites/ghosts/fright"),
            "up":    self.load_safe("assets/sprites/ghosts/fright"),
            "down":  self.load_safe("assets/sprites/ghosts/fright"),
        }

        # BLINK (BLANCO / AZUL)
        self.anim_blink = {
            "left":  self.load_safe("assets/sprites/ghosts/fright_blink"),
            "right": self.load_safe("assets/sprites/ghosts/fright_blink"),
            "up":    self.load_safe("assets/sprites/ghosts/fright_blink"),
            "down":  self.load_safe("assets/sprites/ghosts/fright_blink"),
        }

        # OJOS
        eyes = "assets/sprites/ghosts/eyes"
        self.anim_eyes = {
            "left":  self.load_safe(eyes + "/left"),
            "right": self.load_safe(eyes + "/right"),
            "up":    self.load_safe(eyes + "/up"),
            "down":  self.load_safe(eyes + "/down"),
        }

        # Animación
        self.direction = "left"
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 0.15

        # Dirección inicial
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

    def is_centered(self, tolerance=1.6):
        col, row = self.current_cell()
        cx, cy = self.tile_center(col, row)
        return abs(self.x - cx) <= tolerance and abs(self.y - cy) <= tolerance

    def snap_center_soft(self):
        col, row = self.current_cell()
        cx, cy = self.tile_center(col, row)
        self.x += (cx - self.x) * 0.45
        self.y += (cy - self.y) * 0.45


    # ----------------------------------------------------------
    # SAFE LOADER
    # ----------------------------------------------------------
    def load_safe(self, folder):
        if not os.path.exists(folder):
            return []
        return load_folder(folder, TILE_SIZE)


    # ----------------------------------------------------------
    # COLISIONES CON MUROS
    # ----------------------------------------------------------
    def can_move(self, dx, dy):
        col, row = self.current_cell()
        tcol = col + dx
        trow = row + dy

        # fuera del mapa
        if not (0 <= trow < len(self.level.tiles)):
            return False
        if not (0 <= tcol < len(self.level.tiles[0])):
            return False

        # ¿es muro?
        return not self.level.is_wall(tcol, trow)


    # ----------------------------------------------------------
    # DIRECCIÓN ALEATORIA
    # ----------------------------------------------------------
    def choose_new_direction(self):

        if self.state == "eyes":
            return  # ojos no deben cambiar dirección aleatoriamente

        options = []

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            # evitar retroceder
            if dx == -self.dir_x and dy == -self.dir_y:
                continue
            if self.can_move(dx, dy):
                options.append((dx, dy))

        if not options:
            # retroceder si es la única opción
            if self.can_move(-self.dir_x, -self.dir_y):
                self.dir_x *= -1
                self.dir_y *= -1
            return

        self.dir_x, self.dir_y = random.choice(options)


    # ----------------------------------------------------------
    # ESTADOS
    # ----------------------------------------------------------
    def enter_fright(self):
        if self.state == "eyes":
            return   # ojos no entran a fright

        self.state = "fright"
        self.fright_timer = self.fright_duration
        self.speed = self.fright_speed

        # giro inicial
        self.choose_new_direction()

    def enter_blink(self):
        if self.state == "fright":
            self.state = "blink"

    def enter_eyes(self):
        self.state = "eyes"
        self.speed = self.eyes_speed

        # ir hacia el spawn
        self.dir_x = 0
        self.dir_y = -1

    def reset_normal(self):
        self.state = "normal"
        self.speed = self.base_speed
        self.dir_x, self.dir_y = random.choice([(1,0),(-1,0),(0,1),(0,-1)])


    # ----------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------
    def update(self, dt):
        if self.frozen:
            return

        # --------------------------------
        # FRIGHT / BLINK TIMER
        # --------------------------------
        if self.state in ["fright", "blink"]:
            self.fright_timer -= dt

            if self.state == "fright" and self.fright_timer <= self.blink_threshold:
                self.enter_blink()

            if self.fright_timer <= 0:
                self.reset_normal()

        # --------------------------------
        # EYES MODE (ir directo al spawn)
        # --------------------------------
        if self.state == "eyes":
            dx = 1 if self.spawn_x > self.x else -1 if self.spawn_x < self.x else 0
            dy = 1 if self.spawn_y > self.y else -1 if self.spawn_y < self.y else 0

            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt

            # llegó al spawn
            if abs(self.x - self.spawn_x) < 3 and abs(self.y - self.spawn_y) < 3:
                self.x = self.spawn_x
                self.y = self.spawn_y
                self.reset_normal()

            return  # evitar comportamiento normal

        # --------------------------------
        # MOVIMIENTO NORMAL / FRIGHT / BLINK
        # --------------------------------
        if self.is_centered():
            self.snap_center_soft()
            self.choose_new_direction()

            if not self.can_move(self.dir_x, self.dir_y):
                return

        step = self.speed * dt
        self.x += self.dir_x * step
        self.y += self.dir_y * step

        if self.is_centered():
            self.snap_center_soft()

        # Dirección para sprites
        if self.dir_x < 0:
            self.direction = "left"
        elif self.dir_x > 0:
            self.direction = "right"
        elif self.dir_y < 0:
            self.direction = "up"
        elif self.dir_y > 0:
            self.direction = "down"

        # Animación
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.anim_frame += 1


    # ----------------------------------------------------------
    # DRAW
    # ----------------------------------------------------------
    def draw(self, renderer):

        if self.state == "eyes":
            frames = self.anim_eyes[self.direction]

        elif self.state == "blink":
            frames = self.anim_blink[self.direction]

        elif self.state == "fright":
            frames = self.anim_fright[self.direction]

        else:
            frames = self.anim_normal[self.direction]

        if not frames:
            return

        frame = frames[self.anim_frame % len(frames)]
        renderer.screen.blit(frame, (self.x - TILE_SIZE//2, self.y - TILE_SIZE//2))
