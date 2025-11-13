# entities/entity.py BASE PACMAN
class Entity:
    def __init__(self, x, y, speed=120):
        self.x = x
        self.y = y
        self.speed = speed
        self.dir_x = 0
        self.dir_y = 0

    def update(self, dt):
        self.x += self.dir_x * self.speed * dt
        self.y += self.dir_y * self.speed * dt
