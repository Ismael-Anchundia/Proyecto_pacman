# core/functional_core.py
# Nucleo funcional (puro): helpers independientes de Pygame/IO
from typing import Dict


def resolve_difficulty(presets: Dict[str, Dict[str, float]], name: str, default: str = "NORMAL") -> Dict[str, float]:
    """Funcion pura que selecciona dificultad de forma segura."""
    return presets.get(name, presets[default])


def ghost_speed_for_level(difficulty: Dict[str, float], level: int) -> float:
    """Calculo puro de velocidad de fantasma en funcion del nivel."""
    level = max(1, level)
    base = difficulty["ghost_speed"]
    growth = difficulty["ghost_speed_growth"]
    return base * (growth ** (level - 1))
