# difficulty.py

DIFFICULTY_PRESETS = {
    "EASY": {
        "ghost_speed": 90,
        "ghost_speed_growth": 1.08,   # crecimiento por nivel
        "powerup_duration_factor": 1.4,
    },
    "NORMAL": {
        "ghost_speed": 120,
        "ghost_speed_growth": 1.10,
        "powerup_duration_factor": 1.0,
    },
    "HARD": {
        "ghost_speed": 150,
        "ghost_speed_growth": 1.12,
        "powerup_duration_factor": 0.8,
    },
    "CHAOS": {
        "ghost_speed": 180,
        "ghost_speed_growth": 1.15,
        "powerup_duration_factor": 0.6,
    },
}
