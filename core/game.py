# core/game.py
import pygame
import time
import random

from difficulty import DIFFICULTY_PRESETS

from powerups.speed_boost import SpeedBoost
from powerups.time_freeze import TimeFreeze
from powerups.score_multiplier import ScoreMultiplier
from powerups.fright_mode import FrightMode

import config
from config import FPS, DARK_BLUE
from core.renderer import Renderer, TILE_SIZE
from levels.level import Level
from entities.pacman import Pacman
from entities.ghost import Ghost
from ui.menu import Menu
from ui.hud import HUD


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Pantalla FULLSCREEN
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Pac-Man")

        self.clock = pygame.time.Clock()
        self._running = False

        self.dt = 0
        self.last_time = time.perf_counter()

        # Estado
        self.state = "MENU"

        # Dificultad
        self.difficulty = DIFFICULTY_PRESETS["NORMAL"]
        self.current_level = 1

        self.menu = Menu()
        self.hud = HUD()

        self.ghost_combo = 0

        # Cargar nivel
        self.level = Level("levels/maps/level1.json", game=self)

        # Surface interna
        self.map_width  = len(self.level.tiles[0]) * TILE_SIZE
        self.map_height = len(self.level.tiles) * TILE_SIZE

        self.game_surface = pygame.Surface((self.map_width, self.map_height))
        self.renderer = Renderer(self.game_surface)

        # Pac-Man
        spawn_col, spawn_row = self.level.pacman_spawn
        self.pacman = Pacman(
            spawn_col * TILE_SIZE + TILE_SIZE // 2,
            spawn_row * TILE_SIZE + TILE_SIZE // 2,
            self.level
        )

        # Fantasmas
        self.ghosts = []
        self.ghost_colors = ["red", "pink", "blue", "orange"]
        self.spawn_ghosts_for_level()

    # ================================================================
    # CREACIÓN DE FANTASMAS
    # ================================================================
    def spawn_ghosts_for_level(self, speed=None):

        if speed is None:
            base = self.difficulty["ghost_speed"]
            growth = self.difficulty["ghost_speed_growth"]
            speed = base * (growth ** (self.current_level - 1))

        self.ghosts = []

        for i, (col, row) in enumerate(self.level.ghost_spawns):

            gx = col * TILE_SIZE + TILE_SIZE // 2
            gy = row * TILE_SIZE + TILE_SIZE // 2

            color = self.ghost_colors[i % len(self.ghost_colors)]
            ghost = Ghost(gx, gy, self.level, color=color, speed=speed)

            # Si está en la casita → inicia en modo "house"
            if (col, row) in self.level.ghost_house_area:
                ghost.state = "house"
                ghost.dir_x = 0
                ghost.dir_y = 0
                ghost.house_timer = 0.8 + i * 0.6

            self.ghosts.append(ghost)



    # ================================================================
    # LOOP PRINCIPAL
    # ================================================================
    def run(self):
        self._running = True
        while self._running:
            now = time.perf_counter()
            self.dt = now - self.last_time
            self.last_time = now

            self.handle_events()
            self.update(self.dt)
            self.render()

            self.clock.tick(FPS)

    # ================================================================
    # MANEJO DE EVENTOS
    # ================================================================
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

            if self.state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.menu.move_selection(-1)
                    elif event.key == pygame.K_DOWN:
                        self.menu.move_selection(1)
                    elif event.key == pygame.K_RETURN:
                        self.start_game_with_difficulty()

            if self.state == "GAME_OVER":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = "MENU"

            if self.state == "VICTORY":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = "MENU"

        if self.state == "GAME":
            keys = pygame.key.get_pressed()
            self.pacman.handle_input(keys)

            if keys[pygame.K_p]:
                self.state = "PAUSE"

        if self.state == "PAUSE":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.state = "GAME"

    # ================================================================
    # UPDATE
    # ================================================================
    def update(self, dt):
        if self.state == "GAME":
            self.pacman.update(dt)

            for ghost in self.ghosts:
                ghost.update(dt)

                if self.pacman.collides_with(ghost):

                    if ghost.state == "eyes":
                        continue

                    if ghost.state in ["fright", "blink"]:
                        self.ghost_combo += 1
                        points = 200 * (2 ** (self.ghost_combo - 1))
                        self.hud.add_score(points)
                        ghost.enter_eyes()
                        continue

                    self.ghost_combo = 0
                    self.handle_pacman_hit()
                    return

            if not any(g.state in ["fright", "blink"] for g in self.ghosts):
                self.ghost_combo = 0

        # Nivel completado
        if len(self.level.pellets) == 0 and len(self.level.powerups) == 0:
            self.current_level += 1
            self.load_next_level()

    # ================================================================
    # RENDER — FULLSCREEN + ESCALADO AUTOMÁTICO
    # ================================================================
    def render(self):
        # Dibujar en surface interna
        self.game_surface.fill(DARK_BLUE)

        if self.state == "MENU":
            self.menu.draw(self.renderer)

        elif self.state == "GAME":
            self.draw_gameplay()

        elif self.state == "PAUSE":
            self.draw_gameplay()
            self.renderer.draw_text("PAUSA", 350, 250, (255, 255, 255), 40)

        elif self.state == "GAME_OVER":
            self.renderer.draw_text("GAME OVER", 300, 260, (255, 0, 0), 40)
            self.renderer.draw_text("ENTER para volver", 260, 320, (255, 255, 255), 24)

        elif self.state == "VICTORY":
            self.renderer.draw_text("¡VICTORIA!", 310, 260, (255, 255, 0), 40)

        # ---- ESCALADO ----
        window_w, window_h = self.screen.get_size()
        game_w, game_h = self.game_surface.get_size()

        scale_x = window_w / game_w
        scale_y = window_h / game_h
        scale = min(scale_x, scale_y)

        scaled_w = int(game_w * scale)
        scaled_h = int(game_h * scale)

        scaled_surface = pygame.transform.smoothscale(
            self.game_surface, (scaled_w, scaled_h)
        )

        x = (window_w - scaled_w) // 2
        y = (window_h - scaled_h) // 2

        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled_surface, (x, y))

        pygame.display.flip()

    def draw_gameplay(self):
        self.level.draw(self.renderer)
        self.pacman.draw(self.renderer)

        for ghost in self.ghosts:
            ghost.draw(self.renderer)

        self.hud.draw(self.renderer)

    # ================================================================
    # VIDA PERDIDA
    # ================================================================
    def handle_pacman_hit(self):
        self.hud.lives -= 1

        if self.hud.lives <= 0:
            self.state = "GAME_OVER"
            return

        pygame.time.delay(700)
        self.respawn_entities()

    # ================================================================
    # RESPAWN ENTIDADES
    # ================================================================
    def respawn_entities(self):
        spawn_col, spawn_row = self.level.pacman_spawn
        self.pacman.x = spawn_col * TILE_SIZE + TILE_SIZE // 2
        self.pacman.y = spawn_row * TILE_SIZE + TILE_SIZE // 2

        self.pacman.dir_x = 0
        self.pacman.dir_y = 0
        self.pacman.next_dir_x = 0
        self.pacman.next_dir_y = 0

        self.ghosts.clear()

        base = self.difficulty["ghost_speed"]
        growth = self.difficulty["ghost_speed_growth"]
        speed = base * (growth ** (self.current_level - 1))

        self.spawn_ghosts_for_level(speed=speed)

    # ================================================================
    # REINICIAR PARTIDA
    # ================================================================
    def reset_game(self):
        self.hud.reset()

        self.ghosts.clear()

        self.level = Level("levels/maps/level1.json", game=self)
        self.pacman.level = self.level

        self.respawn_entities()

    # ================================================================
    # POWER-UPS
    # ================================================================
    def freeze_ghosts(self, state):
        for ghost in self.ghosts:
            ghost.frozen = state

    def activate_powerup(self, pacman, col, row):
        p = random.choice([
            SpeedBoost(),
            TimeFreeze(),
            ScoreMultiplier(),
            FrightMode()
        ])
        pacman.add_effect(p)

    # ================================================================
    # INICIO CON DIFICULTAD
    # ================================================================
    def start_game_with_difficulty(self):
        diff_name = self.menu.get_selected_difficulty()
        self.difficulty = DIFFICULTY_PRESETS[diff_name]

        self.current_level = 1
        self.reset_game()
        self.state = "GAME"

    # ================================================================
    # SIGUIENTE NIVEL
    # ================================================================
    def load_next_level(self):
        self.ghosts.clear()

        self.level = Level("levels/maps/level1.json", game=self)
        self.pacman.level = self.level

        self.respawn_entities()
