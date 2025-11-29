# ui/menu.py
import pygame
from dataclasses import dataclass
from typing import List

from config import WHITE, YELLOW, RED


# ------------------------------
# Núcleo funcional (puro)
# ------------------------------
def cycle_option(current: int, delta: int, size: int) -> int:
    """Pure function: cycles the index without mutating input."""
    if size <= 0:
        return 0
    return (current + delta) % size


def reduce_menu_selection(selected: int, action: str, options: List[str]) -> int:
    """Reducer puro para mover la selección según la acción declarativa."""
    deltas = {"UP": -1, "DOWN": 1}
    delta = deltas.get(action, 0)
    return cycle_option(selected, delta, len(options))


@dataclass(frozen=True)
class MenuHint:
    label: str
    description: str


@dataclass(frozen=True)
class MenuItem:
    label: str
    action: str  # start | help | credits | config | exit


class Menu:
    def __init__(self):
        self.title = "PAC-MAN"
        self.items = [
            MenuItem("Iniciar Juego", "start"),
            MenuItem("Ayuda", "help"),
            MenuItem("Creditos", "credits"),
            MenuItem("Configuracion", "config"),
            MenuItem("Salir", "exit"),
        ]
        self.selected = 0
        self.hints = [
            MenuHint("UP / DOWN / W / S", "Mover"),
            MenuHint("ENTER", "Seleccionar"),
            MenuHint("ESC", "Cerrar"),
        ]

    def move_selection(self, direction):
        self.selected = cycle_option(self.selected, direction, len(self.items))

    def handle_action(self, action: str):
        """Shell imperativa que delega en reducer puro."""
        labels = [i.label for i in self.items]
        self.selected = reduce_menu_selection(self.selected, action, labels)

    def get_selected_action(self):
        return self.items[self.selected].action

    def draw(self, renderer):
        screen = renderer.screen
        width, _ = screen.get_size()
        center_x = width // 2

        def draw_center(text, y, color, size):
            font = pygame.font.SysFont(None, size, bold=True)
            surf = font.render(text, True, color)
            rect = surf.get_rect(center=(center_x, y))
            screen.blit(surf, rect)

        # Top score bar
        draw_center("1UP   00      HI-SCORE  10000      2UP   00", 50, WHITE, 24)

        # Logo panel
        logo_rect = pygame.Rect(center_x - 200, 90, 400, 100)
        pygame.draw.rect(screen, (255, 170, 200), logo_rect, border_radius=8)
        draw_center(self.title, logo_rect.centery + 4, YELLOW, 52)

        # Menu options estilo lista principal
        base_y = 240
        for i, item in enumerate(self.items):
            color = YELLOW if i == self.selected else WHITE
            prefix = ">" if i == self.selected else " "
            draw_center(f"{prefix} {item.label}", base_y + i * 40, color, 32)

        # Marca / puntuación
        draw_center("HI-SCORE 5270", 430, WHITE, 20)

        # Hints
        for index, hint in enumerate(self.hints):
            draw_center(f"{hint.label}: {hint.description}", 540 + index * 24, WHITE, 18)
