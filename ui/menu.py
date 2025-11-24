# ui/menu.py
from config import WHITE, YELLOW

class Menu:
    def __init__(self):
        self.title = "PAC-MAN"
        self.options = ["EASY", "NORMAL", "HARD", "CHAOS"]
        self.selected = 1   # NORMAL por defecto

    def move_selection(self, direction):
        self.selected = (self.selected + direction) % len(self.options)

    def get_selected_difficulty(self):
        return self.options[self.selected]

    def draw(self, renderer):
        renderer.draw_text(self.title, 260, 120, WHITE, 48)
        renderer.draw_text("Selecciona dificultad:", 240, 200, WHITE, 28)

        for i, opt in enumerate(self.options):
            color = YELLOW if i == self.selected else WHITE
            renderer.draw_text(opt, 340, 260 + i * 40, color, 32)

        renderer.draw_text("ENTER para iniciar", 280, 420, WHITE, 24)
