# core/game.py
import pygame
import time
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, DARK_BLUE

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # sonido opcional
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self._running = False
        self.dt = 0
        self.last_time = time.perf_counter()

        # Aquí más adelante se inicializarán entidades, niveles, etc.
        # self.player = Pacman()
        # self.level = Level()
        # self.renderer = Renderer()

    def run(self):
        """Bucle principal."""
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
        """Eventos del teclado o cierre."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._running = False

    def update(self, dt):
        """Actualizar lógica del juego."""
        pass  # Aquí luego irá player.update(dt), etc.

    def render(self):
        """Dibuja la escena."""
        self.screen.fill(DARK_BLUE)

        # Texto temporal de FPS
        font = pygame.font.SysFont(None, 26)
        text = font.render(f"FPS: {int(self.clock.get_fps())}", True, (200, 200, 200))
        self.screen.blit(text, (10, 10))

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()
