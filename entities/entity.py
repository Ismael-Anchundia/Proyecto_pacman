# entities/entity.py
import math

class Entity:
    def __init__(self, x, y, speed=100):
        """
        x, y representan SIEMPRE el CENTRO del sprite.
        """
        self.x = x
        self.y = y
        self.speed = speed

        # Para powerups
        self.effects = []
        self.invincible = False
        self.speed_multiplier = 1.0

    # -----------------------------
    # POWERUPS
    # -----------------------------
    def apply_speed_multiplier(self, mul):
        self.speed_multiplier = mul

    def reset_speed(self):
        self.speed_multiplier = 1.0

    # -----------------------------
    # COLISIÓN SIMPLE
    # -----------------------------
    def collides_with(self, other, radius=20):
        """
        Colisión aproximada por distancia entre centros.
        (Pacman tiene su propio método más preciso.)
        """
        return math.dist((self.x, self.y), (other.x, other.y)) < radius
