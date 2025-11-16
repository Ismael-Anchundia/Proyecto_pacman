# ui/menu.py
from config import WHITE

class Menu:
    def __init__(self):
        self.title = "PAC-MAN"
        self.prompt = "Presiona ENTER para comenzar"

    def draw(self, renderer):
        renderer.draw_text(self.title, 260, 200, WHITE, 40)
        renderer.draw_text(self.prompt, 230, 300, WHITE, 24)
