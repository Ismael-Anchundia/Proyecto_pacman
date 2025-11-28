# config.py

# ==========================================================
# CONFIGURACIÓN GENERAL (constantes y valores funcionales)
# ==========================================================

from dataclasses import dataclass

# Tamaño base del tile (se puede cambiar sin romper nada)
TILE_SIZE = 32

# FPS fijo — no debe mutar nunca
FPS = 60

# Título del juego
TITLE = "Pac-Man Power-Up Edition"


# ==========================================================
# DATACLASS FUNCIONAL PARA RESOLUCIÓN DINÁMICA
# ==========================================================

@dataclass
class Resolution:
    width: int
    height: int


# Inicialmente 0 → será actualizada dinámicamente por el mapa
SCREEN_RESOLUTION = Resolution(0, 0)


# ==========================================================
# COLORES (inmutables)
# ==========================================================

BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)
YELLOW     = (255, 255, 0)
RED        = (255, 0, 0)
BLUE       = (0, 0, 255)
GREEN      = (0, 255, 0)
DARK_BLUE  = (10, 10, 30)


# ==========================================================
# RUTAS DE ASSETS
# ==========================================================

ASSETS_DIR  = "assets"
SPRITES_DIR = f"{ASSETS_DIR}/sprites"
SOUNDS_DIR  = f"{ASSETS_DIR}/sounds"
FONTS_DIR   = f"{ASSETS_DIR}/fonts"
LEVELS_DIR  = "levels/maps"
