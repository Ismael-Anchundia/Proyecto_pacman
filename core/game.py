# core/game.py
import pygame
import time
import sys
import random

from difficulty import DIFFICULTY_PRESETS

from powerups.speed_boost import SpeedBoost
from powerups.invincibility import Invincibility
from powerups.time_freeze import TimeFreeze
from powerups.score_multiplier import ScoreMultiplier

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DARK_BLUE
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

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man")

        self.clock = pygame.time.Clock()
        self._running = False

        self.dt = 0
        self.last_time = time.perf_counter()

        # Estados del juego
        self.state = "MENU"

        # Valores iniciales
        self.difficulty = DIFFICULTY_PRESETS["NORMAL"]
        self.current_level = 1

        self.renderer = Renderer(self.screen)
        self.menu = Menu()
        self.hud = HUD()

        # Nivel inicial (placeholder)
        self.level = Level("levels/maps/level1.json", game=self)

        # Crear Pac-Man
        spawn_col, spawn_row = self.level.pacman_spawn
        spawn_x = spawn_col * TILE_SIZE + TILE_SIZE // 2
        spawn_y = spawn_row * TILE_SIZE + TILE_SIZE // 2
        self.pacman = Pacman(spawn_x, spawn_y, level=self.level)

        # Crear fantasmas iniciales
        self.ghosts = []
        for col, row in self.level.ghost_spawns:
            gx = col * TILE_SIZE + TILE_SIZE // 2
            gy = row * TILE_SIZE + TILE_SIZE // 2
            colors = ["red", "pink", "blue", "orange"]
            i = len(self.ghosts) % 4
            self.ghosts.append(Ghost(gx, gy, self.level, color=colors[i]))


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

            # MENÚ
            if self.state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.menu.move_selection(-1)
                    elif event.key == pygame.K_DOWN:
                        self.menu.move_selection(1)
                    elif event.key == pygame.K_RETURN:
                        self.start_game_with_difficulty()

            # GAME OVER → volver menú
            if self.state == "GAME_OVER":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = "MENU"

            # VICTORIA → volver menú
            if self.state == "VICTORY":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = "MENU"

        # Controles durante partida
        if self.state == "GAME":
            keys = pygame.key.get_pressed()
            self.pacman.handle_input(keys)

            if keys[pygame.K_p]:
                self.state = "PAUSE"

        # PAUSA
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

            # Actualizar fantasmas
            for ghost in self.ghosts:
                ghost.update(dt)

                # Colisión Pac-Man ↔ Fantasma
                if self.pacman.collides_with(ghost):

                    # Si está invencible → come fantasma
                    if self.pacman.invincible:
                        self.hud.add_ghost_points()

                        if self.level.ghost_spawns:
                            spawn_col, spawn_row = random.choice(self.level.ghost_spawns)
                            ghost.x = spawn_col * TILE_SIZE + TILE_SIZE // 2
                            ghost.y = spawn_row * TILE_SIZE + TILE_SIZE // 2

                    else:
                        # Pierde vida
                        self.handle_pacman_hit()
                        return

            # ¿Nivel completado?
            if len(self.level.pellets) == 0 and len(self.level.powerups) == 0:
                self.current_level += 1
                self.load_next_level()

    # ================================================================
    # RENDER
    # ================================================================
    def render(self):
        self.screen.fill(DARK_BLUE)

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
    # RESPAWN PAC-MAN Y FANTASMAS
    # ================================================================
    def respawn_entities(self):
        # Respawn Pac-Man
        spawn_col, spawn_row = self.level.pacman_spawn
        self.pacman.x = spawn_col * TILE_SIZE + TILE_SIZE // 2
        self.pacman.y = spawn_row * TILE_SIZE + TILE_SIZE // 2

        self.pacman.dir_x = 0
        self.pacman.dir_y = 0
        self.pacman.next_dir_x = 0
        self.pacman.next_dir_y = 0

        # Respawn Fantasmas con velocidad del nivel
        self.ghosts = []
        base = self.difficulty["ghost_speed"]
        growth = self.difficulty["ghost_speed_growth"]
        speed = base * (growth ** (self.current_level - 1))

        for col, row in self.level.ghost_spawns:
            gx = col * TILE_SIZE + TILE_SIZE // 2
            gy = row * TILE_SIZE + TILE_SIZE // 2
            colors = ["red", "pink", "blue", "orange"]
            i = len(self.ghosts) % 4
            self.ghosts.append(Ghost(gx, gy, self.level, color=colors[i], speed=speed))


    # ================================================================
    # REINICIAR PARTIDA
    # ================================================================
    def reset_game(self):
        self.hud.reset()

        self.level = Level("levels/maps/level1.json", game=self)

        self.pacman.level = self.level
        self.respawn_entities()

    # ================================================================
    # ACTIVAR POWER-UP
    # ================================================================
    def freeze_ghosts(self, state):
        for ghost in self.ghosts:
            ghost.frozen = state
    
    def activate_powerup(self, pacman, col, row):
        p = random.choice([
            SpeedBoost(),
            Invincibility(),
            TimeFreeze(),
            ScoreMultiplier()
        ])
        pacman.add_effect(p)

    # ================================================================
    # INICIO PARTIDA
    # ================================================================
    def start_game_with_difficulty(self):
        diff_name = self.menu.get_selected_difficulty()
        self.difficulty = DIFFICULTY_PRESETS[diff_name]

        self.current_level = 1
        self.reset_game()
        self.state = "GAME"

    # ================================================================
    # CARGAR SIGUIENTE NIVEL
    # ================================================================
    def load_next_level(self):
    # En vez de cambiar de archivo, solo recarga el mismo mapa
        self.level = Level("levels/maps/level1.json", game=self)
        self.pacman.level = self.level
        self.respawn_entities()


        # Actualizar referencias
        self.pacman.level = self.level
        self.respawn_entities()
