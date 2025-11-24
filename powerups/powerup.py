# powerups/powerup.py

class PowerUp:
    def __init__(self, duration):
        self.duration = duration
        self.remaining_time = duration

    def apply(self, pacman):
        pass

    def remove(self, pacman):
        pass
