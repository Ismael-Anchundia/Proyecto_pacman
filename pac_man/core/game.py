# core/game.py
import pygame
import time
import sys

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

        # Estado inicial
        self.state = "MENU"

        self.renderer = Renderer(self.screen)
        self.menu = Menu()
        self.hud = HUD()

        # Cargar nivel
        self.level = Level("levels/maps/level1.txt", game=self)

        # Instanciar Pac-Man
        spawn_col, spawn_row = self.level.pacman_spawn
        spawn_x = spawn_col * TILE_SIZE + TILE_SIZE // 2
        spawn_y = spawn_row * TILE_SIZE + TILE_SIZE // 2

        self.pacman = Pacman(spawn_x, spawn_y, level=self.level)

        # Instanciar fantasmas
        self.ghosts = []
        for col, row in self.level.ghost_spawns:
            gx = col * TILE_SIZE + TILE_SIZE // 2
            gy = row * TILE_SIZE + TILE_SIZE // 2
            self.ghosts.append(Ghost(gx, gy, self.level))

    # --------------------------------------
    # LOOP PRINCIPAL
    # --------------------------------------
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

    # --------------------------------------
    # MANEJO DE EVENTOS
    # --------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

            # MENÚ → GAME
            if self.state == "MENU":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.reset_game()
                    self.state = "GAME"

            # GAME OVER → MENU
            if self.state == "GAME_OVER":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.reset_game()
                    self.state = "MENU"

            # VICTORIA → MENU
            if self.state == "VICTORY":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.reset_game()
                    self.state = "MENU"

        # Controles de juego
        if self.state == "GAME":
            keys = pygame.key.get_pressed()
            self.pacman.handle_input(keys)

            if keys[pygame.K_p]:
                self.state = "PAUSE"

        if self.state == "PAUSE":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.state = "GAME"

    # --------------------------------------
    # UPDATE
    # --------------------------------------
    def update(self, dt):
        if self.state == "GAME":
            self.pacman.update(dt)

            for ghost in self.ghosts:
                ghost.update(dt)

                if self.pacman.collides_with(ghost):
                    self.handle_pacman_hit()
                    return

            # Condición de victoria
            if len(self.level.pellets) == 0 and len(self.level.powerups) == 0:
                self.state = "VICTORY"

    # --------------------------------------
    # RENDER
    # --------------------------------------
    def render(self):
        self.screen.fill(DARK_BLUE)

        if self.state == "MENU":
            self.menu.draw(self.renderer)

        elif self.state == "GAME":
            self.draw_gameplay()

        elif self.state == "PAUSE":
            self.draw_gameplay()
            self.renderer.draw_text("PAUSA", 350, 250, (255, 255, 255), 40)
            self.renderer.draw_text("Presiona R para continuar", 250, 310, (255, 255, 255), 24)

        elif self.state == "GAME_OVER":
            self.renderer.draw_text("GAME OVER", 300, 260, (255, 0, 0), 40)
            self.renderer.draw_text("ENTER para volver al menú", 220, 320, (255, 255, 255), 24)

        elif self.state == "VICTORY":
            self.renderer.draw_text("¡VICTORIA!", 310, 260, (255, 255, 0), 40)
            self.renderer.draw_text("ENTER para volver al menú", 220, 320, (255, 255, 255), 24)

        pygame.display.flip()

    def draw_gameplay(self):
        self.level.draw(self.renderer)
        self.pacman.draw(self.renderer)

        for ghost in self.ghosts:
            ghost.draw(self.renderer)

        self.hud.draw(self.renderer)

    # --------------------------------------
    # PERDER UNA VIDA
    # --------------------------------------
    def handle_pacman_hit(self):
        self.hud.lives -= 1

        if self.hud.lives <= 0:
            self.state = "GAME_OVER"
            return

        pygame.time.delay(700)
        self.respawn_entities()

    # --------------------------------------
    # RESPAWN PAC-MAN Y FANTASMAS
    # --------------------------------------
    def respawn_entities(self):
        self.pacman.level = self.level  # FIX IMPORTANTE

        spawn_col, spawn_row = self.level.pacman_spawn
        self.pacman.x = spawn_col * TILE_SIZE + TILE_SIZE // 2
        self.pacman.y = spawn_row * TILE_SIZE + TILE_SIZE // 2

        self.pacman.dir_x = 0
        self.pacman.dir_y = 0
        self.pacman.next_dir_x = 0
        self.pacman.next_dir_y = 0

        # Fantasmas
        self.ghosts = []
        for col, row in self.level.ghost_spawns:
            gx = col * TILE_SIZE + TILE_SIZE // 2
            gy = row * TILE_SIZE + TILE_SIZE // 2
            self.ghosts.append(Ghost(gx, gy, self.level))

    # --------------------------------------
    # REINICIAR TODO EL JUEGO
    # --------------------------------------
    def reset_game(self):
        self.hud.reset()
        self.level = Level("levels/maps/level1.txt", game=self)

        # FIX IMPORTANTE: Pac-Man debe apuntar al nuevo nivel
        self.pacman.level = self.level

        # Respawn Pac-Man
        spawn_col, spawn_row = self.level.pacman_spawn
        self.pacman.x = spawn_col * TILE_SIZE + TILE_SIZE // 2
        self.pacman.y = spawn_row * TILE_SIZE + TILE_SIZE // 2

        # Respawn fantasmas
        self.ghosts = []
        for col, row in self.level.ghost_spawns:
            gx = col * TILE_SIZE + TILE_SIZE // 2
            gy = row * TILE_SIZE + TILE_SIZE // 2
            self.ghosts.append(Ghost(gx, gy, self.level))
