# ui/hud.py
from config import WHITE

class HUD:
    def __init__(self):
        self.score = 0
        self.lives = 3

    def add_score(self, amount):
        self.score += amount

    def reset(self):
        self.score = 0
        self.lives = 3

    def draw(self, renderer):
        renderer.draw_text(f"Score: {self.score}", 10, 10, WHITE, 24)
        renderer.draw_text(f"Lives: {self.lives}", 690, 10, WHITE, 24)
