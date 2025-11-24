# powerups/speed_boost.py
from powerups.powerup import PowerUp

class SpeedBoost(PowerUp):
    def __init__(self):
        super().__init__(duration=6.0)

    def apply(self, pacman):
        pacman.speed_multiplier = 1.8

    def remove(self, pacman):
        pacman.speed_multiplier = 1.0
