# levels/level_loader.py
import json

def load_level_file(path):
    """
    Detecta automáticamente si el archivo es .txt o .json
    y retorna un diccionario con los datos del nivel.
    """
    if path.endswith(".json"):
        return load_json_level(path)
    else:
        return load_txt_level(path)


# -------------------------
# CARGA DE MAPA TXT
# -------------------------
def load_txt_level(path):
    data = {
        "tiles": [],
        "pacman_spawn": [1, 1],
        "ghost_spawns": [],
        "pellets": [],
        "powerups": []
    }

    with open(path, "r") as f:
        for row_index, line in enumerate(f):
            row = line.rstrip("\n")
            data["tiles"].append(row)

            for col_index, char in enumerate(row):
                if char == ".":
                    data["pellets"].append([col_index, row_index])
                elif char == "o":
                    data["powerups"].append([col_index, row_index])
                elif char == "P":
                    data["pacman_spawn"] = [col_index, row_index]
                elif char == "G":
                    data["ghost_spawns"].append([col_index, row_index])

    return data


# -------------------------
# CARGA DE MAPA JSON
# -------------------------
def load_json_level(path):
    with open(path, "r") as f:
        level_data = json.load(f)

    # Validamos estructura mínima
    if "tiles" not in level_data:
        raise ValueError("El JSON debe contener una lista 'tiles'.")

    # Completar campos opcionales con defaults
    level_data.setdefault("pacman_spawn", [1, 1])
    level_data.setdefault("ghost_spawns", [])
    level_data.setdefault("pellets", [])
    level_data.setdefault("powerups", [])

    # Si el JSON no incluye pellets, los generamos desde el layout
    if len(level_data["pellets"]) == 0:
        for row_idx, row in enumerate(level_data["tiles"]):
            for col_idx, char in enumerate(row):
                if char == ".":
                    level_data["pellets"].append([col_idx, row_idx])
                if char == "o":
                    level_data["powerups"].append([col_idx, row_idx])
                if char == "G":
                    level_data["ghost_spawns"].append([col_idx, row_idx])
                if char.upper() == "P":
                    level_data["pacman_spawn"] = [col_idx, row_idx]

    return level_data
