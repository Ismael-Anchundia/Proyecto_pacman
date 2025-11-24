import pygame
import os

def load_sprite(path, size):
    """Carga una imagen individual y la escala a size."""
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (size, size))

def load_folder(folder_path, size):
    """Carga todos los png del folder y los escala."""
    frames = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".png"):
            img = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
            img = pygame.transform.scale(img, (size, size))
            frames.append(img)
    return frames
