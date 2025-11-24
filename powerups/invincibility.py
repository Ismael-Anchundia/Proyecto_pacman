# powerups/invincibility.py
from powerups.powerup import PowerUp

class Invincibility(PowerUp):
    def __init__(self):
        super().__init__(duration=5.0)

    def apply(self, pacman):
        pacman.invincible = True

    def remove(self, pacman):
        pacman.invincible = False
