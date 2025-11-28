# entities/ghost.py
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

        # Velocidades por estado
        self.base_speed = speed
        self.fright_speed = speed * 0.7
        self.eyes_speed = speed * 1.7

        # Estados
        self.state = "normal"      # normal | fright | blink | eyes | house
        self.fright_timer = 0.0
        self.fright_duration = 6.0
        self.blink_threshold = 2.0

        # Spawn real (para ojos)
        self.spawn_x = x
        self.spawn_y = y

        # Sprites
        base = f"assets/sprites/ghosts/{color}"
        self.anim_normal = {
            "left":  self.load_safe(base + "/left"),
            "right": self.load_safe(base + "/right"),
            "up":    self.load_safe(base + "/up"),
            "down":  self.load_safe(base + "/down"),
        }

        if all(len(fr) == 0 for fr in self.anim_normal.values()):
            frames = self.load_safe(base)
            self.anim_normal = {d: frames for d in ["left", "right", "up", "down"]}

        self.anim_fright = {d: self.load_safe("assets/sprites/ghosts/fright")
                            for d in ["left", "right", "up", "down"]}

        self.anim_blink = {d: self.load_safe("assets/sprites/ghosts/fright_blink")
                           for d in ["left", "right", "up", "down"]}

        eyes = "assets/sprites/ghosts/eyes"
        self.anim_eyes = {
            "left": self.load_safe(eyes + "/left"),
            "right": self.load_safe(eyes + "/right"),
            "up": self.load_safe(eyes + "/up"),
            "down": self.load_safe(eyes + "/down"),
        }

        # Animación
        self.direction = "left"
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.15

        # Dirección inicial
        self.dir_x, self.dir_y = random.choice([(1,0), (-1,0), (0,1), (0,-1)])


    # ----------------------------------------------------------
    # HELPERS
    # ----------------------------------------------------------
    def load_safe(self, folder):
        return load_folder(folder, TILE_SIZE) if os.path.exists(folder) else []

    def current_cell(self):
        return int(self.x // TILE_SIZE), int(self.y // TILE_SIZE)

    def tile_center(self, col, row):
        return (
            col * TILE_SIZE + TILE_SIZE / 2,
            row * TILE_SIZE + TILE_SIZE / 2
        )


    # ----------------------------------------------------------
    # MOVIMIENTO Y COLISIONES
    # ----------------------------------------------------------
    def can_move(self, dx, dy):
        col, row = self.current_cell()
        tcol = col + dx
        trow = row + dy

        # ------------------------------------------------------
        # 1) FUERA DE RANGO (mapa)
        # ------------------------------------------------------
        if trow < 0 or trow >= len(self.level.tiles):
            return False
        if tcol < 0 or tcol >= len(self.level.tiles[0]):
            return False

        # ------------------------------------------------------
        # 2) DENTRO DE LA CASITA → SOLO PUEDE SALIR POR LA PUERTA
        # ------------------------------------------------------
        inside_house = (col, row) in self.level.ghost_house_area
        at_door = (tcol, trow) == self.level.ghost_house_door

        if inside_house:
            return at_door  # solo salida vertical por la puerta

        # ------------------------------------------------------
        # 3) MODO OJOS → ignora puerta y casita
        # ------------------------------------------------------
        if self.state == "eyes":
            return True

        # ------------------------------------------------------
        # 4) FANTASMA NORMAL NO PUEDE ENTRAR A LA CASITA
        # ------------------------------------------------------
        if (tcol, trow) in self.level.ghost_house_area:
            return False

        # ------------------------------------------------------
        # 5) PARED NORMAL
        # ------------------------------------------------------
        return not self.level.is_wall(tcol, trow)



    def choose_new_direction(self):
        options = []
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            if dx == -self.dir_x and dy == -self.dir_y:
                continue
            if self.can_move(dx, dy):
                options.append((dx, dy))

        if options:
            self.dir_x, self.dir_y = random.choice(options)
        else:
            # Reversa forzada
            if self.can_move(-self.dir_x, -self.dir_y):
                self.dir_x *= -1
                self.dir_y *= -1
            else:
                self.dir_x, self.dir_y = random.choice([(1,0),(-1,0),(0,1),(0,-1)])


    # ----------------------------------------------------------
    # ESTADOS
    # ----------------------------------------------------------
    def enter_fright(self):
        if self.state == "eyes":
            return
        self.state = "fright"
        self.fright_timer = self.fright_duration
        self.speed = self.fright_speed
        self.dir_x *= -1
        self.dir_y *= -1

    def enter_blink(self):
        if self.state == "fright":
            self.state = "blink"

    def enter_eyes(self):
        self.state = "eyes"
        self.speed = self.eyes_speed

    def exit_fright(self):
        self.state = "normal"
        self.speed = self.base_speed

    def exit_eyes(self):
        self.state = "normal"
        self.speed = self.base_speed


    # ----------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------
    def update(self, dt):
        if self.frozen:
            return

        # Modo casita
        if self.state == "house":
            return self.update_house(dt)

        # Modo ojos
        if self.state == "eyes":
            return self.update_eyes(dt)

        # Manejo fright/blink
        if self.state in ["fright", "blink"]:
            self.fright_timer -= dt
            if self.state == "fright" and self.fright_timer <= self.blink_threshold:
                self.enter_blink()
            if self.fright_timer <= 0:
                self.exit_fright()

        self.update_walk(dt)


    # ----------------------------------------------------------
    # WALK
    # ----------------------------------------------------------
    def update_walk(self, dt):

        move_step = self.speed * dt

        col, row = self.current_cell()
        cx, cy = self.tile_center(col, row)

        dist_x = cx - self.x
        dist_y = cy - self.y

        # 1. Si está cerca del centro → SNAP SUAVE + cambio de dirección
        if abs(dist_x) <= 1.2 and abs(dist_y) <= 1.2:

            # Snap suave
            self.x += dist_x * 0.35
            self.y += dist_y * 0.35

            self.choose_new_direction()

        # 2. Overshoot prevention (misma lógica que Pac-Man)
        limit = abs(dist_x) if self.dir_x != 0 else abs(dist_y)

        if move_step > limit >= 0.1:

            # Llegar al centro sin pasarse
            self.x += self.dir_x * limit
            self.y += self.dir_y * limit

            # Snap suave (nada de teletransporte)
            self.x += (cx - self.x) * 0.35
            self.y += (cy - self.y) * 0.35

            leftover = move_step - limit

            if self.can_move(self.dir_x, self.dir_y):
                self.x += self.dir_x * leftover
                self.y += self.dir_y * leftover

            return

        # 3. Movimiento normal
        nx = self.x + self.dir_x * move_step
        ny = self.y + self.dir_y * move_step

        if self.can_move(self.dir_x, self.dir_y):
            self.x = nx
            self.y = ny
        else:
            # Snap suave para evitar rebotes raros
            self.x += dist_x * 0.35
            self.y += dist_y * 0.35

        # 4. Sprite direction
        if self.dir_x < 0: self.direction = "left"
        elif self.dir_x > 0: self.direction = "right"
        elif self.dir_y < 0: self.direction = "up"
        elif self.dir_y > 0: self.direction = "down"

        # 5. Animación
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.anim_frame += 1




    # ----------------------------------------------------------
    # HOUSE MODE
    # ----------------------------------------------------------
    def update_house(self, dt):
        self.house_timer -= dt
        if self.house_timer > 0:
            return

        # Salir hacia arriba
        self.dir_x = 0
        self.dir_y = -1
        step = self.speed * dt
        self.y += self.dir_y * step

        col, row = self.current_cell()

        # En cuanto sale → normal
        if (col, row) not in self.level.ghost_house_area:
            self.state = "normal"


    # ----------------------------------------------------------
    # EYES MODE
    # ----------------------------------------------------------
    def update_eyes(self, dt):
        sx, sy = self.spawn_x, self.spawn_y

        # Regresa al spawn
        step = self.eyes_speed * dt
        dx = 1 if sx > self.x else -1 if sx < self.x else 0
        dy = 1 if sy > self.y else -1 if sy < self.y else 0

        self.x += dx * step
        self.y += dy * step

        if abs(self.x - sx) < 2 and abs(self.y - sy) < 2:
            self.x, self.y = sx, sy
            self.exit_eyes()

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

        frame = frames[self.anim_frame % len(frames)]
        renderer.screen.blit(
            frame,
            (self.x - TILE_SIZE // 2, self.y - TILE_SIZE // 2)
        )
