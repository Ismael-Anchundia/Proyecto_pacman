# ui/menu.py
from config import WHITE

class Menu:
    def __init__(self):
        self.title = "PAC-MAN POWER-UP EDITION"
        self.prompt = "Presiona ENTER para empezar"

    def draw(self, renderer):
        renderer.draw_text(self.title, 150, 150, WHITE, 40)
        renderer.draw_text(self.prompt, 180, 250, WHITE, 28)
