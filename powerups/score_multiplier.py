# powerups/score_multiplier.py
from powerups.powerup import PowerUp

class ScoreMultiplier(PowerUp):
    def __init__(self):
        super().__init__(duration=8.0)

    def apply(self, pacman):
        pacman.score_multiplier = 2.0

    def remove(self, pacman):
        pacman.score_multiplier = 1.0
