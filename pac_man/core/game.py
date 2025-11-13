# core/game.py
import pygame
import time
import sys

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DARK_BLUE
from core.renderer import Renderer, TILE_SIZE
from levels.level import Level
from entities.pacman import Pacman
from ui.menu import Menu   # <-- IMPORTANTE

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man Sprint 1")

        self.clock = pygame.time.Clock()
        self._running = False
        self.dt = 0
        self.last_time = time.perf_counter()

        # Estados: MENU → GAME
        self.state = "MENU"

        # Crear renderer
        self.renderer = Renderer(self.screen)

        # Crear menú
        self.menu = Menu()

        # Cargar nivel
        self.level = Level("levels/maps/level1.txt")

        # Pac-Man en coordenadas iniciales
        self.pacman = Pacman(100, 100)

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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

            # --- EVENTOS DEL MENÚ ---
            if self.state == "MENU":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = "GAME"

        # --- EVENTOS DEL JUEGO ---
        if self.state == "GAME":
            keys = pygame.key.get_pressed()
            self.pacman.handle_input(keys)

    def update(self, dt):
        if self.state == "GAME":
            self.pacman.update(dt)

    def render(self):
        self.screen.fill(DARK_BLUE)

        if self.state == "MENU":
            self.menu.draw(self.renderer)

        elif self.state == "GAME":
            self.level.draw(self.renderer)
            self.pacman.draw(self.renderer)

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()
