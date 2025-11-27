# powerups/fright_mode.py

class FrightMode:
    """
    Power-up: Fantasmas entran en modo FRIGHT.
    Pac-Man puede comerlos.
    Dura X segundos.
    """
    def __init__(self, duration=6):
        self.duration = duration
        self.remaining_time = duration

    def apply(self, pacman):
        """Activa fright mode en TODOS los fantasmas."""
        game = pacman.level.game

        for ghost in game.ghosts:
            # Si un fantasma ya está "eyes", no entra en fright
            if ghost.state != "eyes":
                ghost.enter_fright()

    def remove(self, pacman):
        """Cuando termina el efecto, volverán solos a normal por su timer interno."""
        # No se hace nada aquí.
        # ghost.reset_normal() ocurre automáticamente cuando su fright_timer llega a 0.
        pass
