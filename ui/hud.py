# ui/hud.py
from config import WHITE

class HUD:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.ghost_combo = 0  # Combo de fantasmas comidos en invencibilidad

    def add_score(self, amount):
        self.score += amount

    def add_ghost_points(self):
        """Sistema clásico: 200 → 400 → 800 → 1600"""
        combo_values = [200, 400, 800, 1600]
        points = combo_values[min(self.ghost_combo, 3)]
        self.score += points
        self.ghost_combo += 1
        return points

    def reset_ghost_combo(self):
        self.ghost_combo = 0

    def reset(self):
        self.score = 0
        self.lives = 3
        self.ghost_combo = 0

    def draw(self, renderer):
        renderer.draw_text(f"Score: {self.score}", 10, 10, WHITE, 24)
        renderer.draw_text(f"Lives: {self.lives}", 690, 10, WHITE, 24)
