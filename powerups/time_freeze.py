# powerups/time_freeze.py
from powerups.powerup import PowerUp

class TimeFreeze(PowerUp):
    def __init__(self):
        super().__init__(duration=4.0)

    def apply(self, pacman):
        pacman.level.game.freeze_ghosts(True)

    def remove(self, pacman):
        pacman.level.game.freeze_ghosts(False)
