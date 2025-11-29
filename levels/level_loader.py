# levels/level_loader.py
import json
from functools import partial


def read_file(path):
    """Pura: solo lee texto."""
    with open(path, "r") as f:
        return f.readlines()


def parse_txt_lines(lines):
    """Pura: convierte líneas TXT en estructura de nivel."""
    tiles = tuple(line.rstrip("\n") for line in lines)

    pellets = []
    powerups = []
    ghost_spawns = []
    pacman_spawn = (1, 1)

    for r, row in enumerate(tiles):
        for c, ch in enumerate(row):
            if ch == ".":
                pellets.append((c, r))
            elif ch == "o":
                powerups.append((c, r))
            elif ch == "P":
                pacman_spawn = (c, r)
            elif ch == "G":
                ghost_spawns.append((c, r))

    return {
        "tiles": tiles,
        "pellets": tuple(pellets),
        "powerups": tuple(powerups),
        "ghost_spawns": tuple(ghost_spawns),
        "pacman_spawn": pacman_spawn,
    }


def load_txt_level(path):
    return parse_txt_lines(read_file(path))


def load_json_level(path):
    with open(path, "r") as f:
        data = json.load(f)

    if "tiles" not in data:
        raise ValueError("El JSON debe contener una lista 'tiles'.")

    tiles = tuple(data["tiles"])
    pellets = tuple(tuple(p) for p in data.get("pellets", []))
    powerups = tuple(tuple(p) for p in data.get("powerups", []))
    ghost_spawns = tuple(tuple(p) for p in data.get("ghost_spawns", []))
    pacman_spawn = tuple(data.get("pacman_spawn", (1, 1)))

    # Autogenerar pellets si no existen
    if len(pellets) == 0 and len(powerups) == 0:
        gen_p = []
        gen_o = []
        for r, row in enumerate(tiles):
            for c, ch in enumerate(row):
                if ch == ".":
                    gen_p.append((c, r))
                elif ch == "o":
                    gen_o.append((c, r))
        pellets = tuple(gen_p)
        powerups = tuple(gen_o)

    return {
        "tiles": tiles,
        "pellets": pellets,
        "powerups": powerups,
        "ghost_spawns": ghost_spawns,
        "pacman_spawn": pacman_spawn,
    }


# ==========================================================
# SELECCIÓN AUTOMÁTICA
# ==========================================================

def load_level_file(path):
    return load_json_level(path) if path.endswith(".json") else load_txt_level(path)
