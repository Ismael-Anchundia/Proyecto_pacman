# core/game.py
import os
import pygame
import time
import random

from difficulty import DIFFICULTY_PRESETS

from powerups.speed_boost import SpeedBoost
from powerups.time_freeze import TimeFreeze
from powerups.score_multiplier import ScoreMultiplier
from powerups.fright_mode import FrightMode

import config
from config import FPS, DARK_BLUE
from core.renderer import Renderer, TILE_SIZE
from levels.level import Level
from entities.pacman import Pacman
from entities.ghost import Ghost
from ui.menu import Menu
from ui.hud import HUD
from core.functional_core import ghost_speed_for_level, resolve_difficulty


class SoundManager:
    """
    Gestor simple de sonidos. Intenta cargar WAV y si no existe intenta MP3.
    Proporciona metodos semanticos para reproducir los efectos.
    """

    DEFAULT_VOLUME = 0.6

    def __init__(self, base_path="assets/sounds"):
        # Pre-initialize mixer para reducir latencia (opcional)
        try:
            pygame.mixer.pre_init(44100, -16, 1, 512)
        except Exception:
            pass

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.base_path = base_path
        self.sounds = {}
        # nombres esperados (agrega 'step' para caminar)
        self.expected = [
            "waka",
            "power_pellet",
            "frightened",
            "ghost_eaten",
            "death",
            "fruit",
            "ghost_exit",
            "tunnel",
            "intro",
            "step",
        ]
        self.load_all()

    def _path_variants(self, name):
        # Trata de buscar .wav primero, luego .mp3
        return [
            os.path.join(self.base_path, f"{name}.wav"),
            os.path.join(self.base_path, f"{name}.mp3"),
            os.path.join(self.base_path, f"{name}.ogg"),
        ]

    def load(self, name):
        paths = self._path_variants(name)
        loaded = False
        for p in paths:
            if os.path.isfile(p):
                try:
                    snd = pygame.mixer.Sound(p)
                    snd.set_volume(self.DEFAULT_VOLUME)
                    self.sounds[name] = snd
                    loaded = True
                    break
                except Exception as e:
                    print(f"[SoundManager] Error cargando {p}: {e}")
        if not loaded:
            # fallback -> None (no rompe si no existe)
            print(f"[SoundManager] No se encontró sonido para '{name}' (buscado: {paths})")
            self.sounds[name] = None

    def load_all(self):
        for n in self.expected:
            self.load(n)

    def play(self, name, loops=0):
        snd = self.sounds.get(name)
        if snd:
            try:
                # No reproducir si ya hay una instancia sonando
                if snd.get_num_channels() == 0:
                    snd.play(loops=loops)
            except Exception as e:
                print(f"[SoundManager] Error reproducir {name}: {e}")


    def stop(self, name):
        snd = self.sounds.get(name)
        if snd:
            try:
                snd.stop()
            except Exception:
                pass

    # Helpers semánticos
    def play_waka(self):
        self.play("waka")

    def play_power(self):
        self.play("power_pellet")
        # start frightened loop if available
        self.play("frightened", loops=-1)

    def stop_frightened(self):
        self.stop("frightened")

    def play_ghost_eaten(self):
        self.play("ghost_eaten")

    def play_death(self):
        self.play("death")

    def play_fruit(self):
        self.play("fruit")

    def play_ghost_exit(self):
        self.play("ghost_exit")

    def play_tunnel(self):
        self.play("tunnel")

    def play_intro(self):
        self.play("intro")

    def play_step(self):
        """Sonido de pasos / caminar."""
        self.play("step")


class Game:
    def __init__(self):
        # Inicialización principal
        pygame.init()
        # SoundManager inicializa o asegura mixer
        self.sfx = SoundManager(base_path="assets/sounds")

        # Ventana en modo ventana (no fullscreen) para ver controles y boton de cierre
        self.window_size = (640, 720)
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        pygame.display.set_caption("Pac-Man")

        self.clock = pygame.time.Clock()
        self._running = False

        self.dt = 0.0
        self.last_time = time.perf_counter()

        # Estado
        self.state = "MENU"   # MENU, GAME, PAUSE, GAME_OVER, VICTORY

        # Dificultad default
        self.difficulty = DIFFICULTY_PRESETS["NORMAL"]
        self.current_level = 1

        self.menu = Menu()
        self.hud = HUD()
        self.menu_overlay = None

        self.ghost_combo = 0

        # Cargar nivel
        self.level = Level("levels/maps/level1.json", game=self)

        # Surface interna
        self.map_width = len(self.level.tiles[0]) * TILE_SIZE
        self.map_height = len(self.level.tiles) * TILE_SIZE

        self.game_surface = pygame.Surface((self.map_width, self.map_height))
        self.renderer = Renderer(self.game_surface)

        # Pac-Man
        spawn_col, spawn_row = self.level.pacman_spawn
        self.pacman = Pacman(
            spawn_col * TILE_SIZE + TILE_SIZE // 2,
            spawn_row * TILE_SIZE + TILE_SIZE // 2,
            self.level
        )

        # Fantasmas
        self.ghosts = []
        self.ghost_colors = ["red", "pink", "blue", "orange"]
        self.spawn_ghosts_for_level()

        # Variables para sonido de pasos
        # lleva la posición previa de pacman para detectar movimiento
        self._prev_pacman_pos = (self.pacman.x, self.pacman.y)
        # temporizador para espaciar pasos (segundos). Ajusta para ritmo.
        self.step_interval = 0.12
        self._step_timer = 0.0

    # ================================================================
    # CREAR FANTASMAS
    # ================================================================
    def spawn_ghosts_for_level(self, speed=None):

        if speed is None:
            speed = ghost_speed_for_level(self.difficulty, self.current_level)

        self.ghosts = []

        for i, (col, row) in enumerate(self.level.ghost_spawns):

            gx = col * TILE_SIZE + TILE_SIZE // 2
            gy = row * TILE_SIZE + TILE_SIZE // 2

            color = self.ghost_colors[i % len(self.ghost_colors)]
            ghost = Ghost(gx, gy, self.level, color=color, speed=speed)

            # Fantasmas dentro de la casita
            if (col, row) in self.level.ghost_house_area:
                ghost.state = "house"
                ghost.dir_x = 0
                ghost.dir_y = 0
                ghost.house_timer = 0.8 + i * 0.6

            self.ghosts.append(ghost)

    # ================================================================
    # LOOP PRINCIPAL
    # ================================================================
    def run(self):
        self._running = True
        while self._running:
            now = time.perf_counter()
            self.dt = now - self.last_time
            self.last_time = now

            self.handle_events()
            self.update(self.dt)
            self.render()

            self.clock.tick(FPS)

    # ================================================================
    # EVENTOS
    # ================================================================
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

            if self.state == "MENU" and event.type == pygame.KEYDOWN:
                # Si hay overlay, permitir cerrarlo con Enter o Backspace
                if self.menu_overlay and event.key in (pygame.K_RETURN, pygame.K_BACKSPACE):
                    self.menu_overlay = None
                    return

                menu_actions = {
                    pygame.K_UP: lambda: self.menu.handle_action("UP"),
                    pygame.K_DOWN: lambda: self.menu.handle_action("DOWN"),
                    pygame.K_w: lambda: self.menu.handle_action("UP"),
                    pygame.K_s: lambda: self.menu.handle_action("DOWN"),
                    pygame.K_a: lambda: self.menu.handle_action("UP"),
                    pygame.K_d: lambda: self.menu.handle_action("DOWN"),
                }
                handler = menu_actions.get(event.key)
                if handler:
                    handler()

                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.start_menu_selection()
                    return

                if event.key == pygame.K_ESCAPE:
                    self._running = False

            if self.state == "GAME_OVER":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = "MENU"

            if self.state == "VICTORY":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = "MENU"

        # Juego
        if self.state == "GAME":
            keys = pygame.key.get_pressed()
            # delegar entrada a Pac-Man (no tocamos su lógica)
            self.pacman.handle_input(keys)

            if keys[pygame.K_p]:
                self.state = "PAUSE"

        # Pausa
        if self.state == "PAUSE":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.state = "GAME"

    # ================================================================
    # UPDATE
    # ================================================================
    def update(self, dt):
        if self.state == "GAME":
            # Actualizamos Pac-Man
            self.pacman.update(dt)

            # --- detección de movimiento para sonido de pasos ---
            # comparamos posición actual vs previa; si cambió y no estamos en estados especiales,
            # reproducimos pasos en intervalo definido.
            cur_pos = (self.pacman.x, self.pacman.y)
            moved = (abs(cur_pos[0] - self._prev_pacman_pos[0]) > 0.1 or
                     abs(cur_pos[1] - self._prev_pacman_pos[1]) > 0.1)

            # sólo si el juego está corriendo y Pac-Man se mueve
            if moved:
                self._step_timer += dt
                if self._step_timer >= self.step_interval:
                    # reproducir sonido de paso
                    self.sfx.play_step()
                    self._step_timer = 0.0
            else:
                # reset timer si no se mueve
                self._step_timer = self.step_interval

            self._prev_pacman_pos = cur_pos

            # --- resto de updates (fantasmas, colisiones) ---
            for ghost in self.ghosts:
                ghost.update(dt)

                # colisión con fantasma
                if self.pacman.collides_with(ghost):

                    if ghost.state == "eyes":
                        continue

                    if ghost.state in ["fright", "blink"]:
                        self.ghost_combo += 1
                        points = 200 * (2 ** (self.ghost_combo - 1))
                        self.hud.add_score(points)

                        # Sonido de fantasma comido
                        self.sfx.play_ghost_eaten()

                        ghost.enter_eyes()
                        continue

                    self.ghost_combo = 0

                    # Sonido de muerte
                    self.sfx.play_death()
                    self.handle_pacman_hit()
                    return

            # si no quedan asustados, reset combo
            if not any(g.state in ["fright", "blink"] for g in self.ghosts):
                self.ghost_combo = 0

        # Nivel completado
        if len(self.level.pellets) == 0 and len(self.level.powerups) == 0:
            self.current_level += 1
            self.load_next_level()

    # ================================================================
    # RENDER
    # ================================================================
    def render(self):
        self.game_surface.fill(DARK_BLUE)

        if self.state == "MENU":
            self.draw_menu()

        elif self.state == "GAME":
            self.draw_gameplay()

        elif self.state == "PAUSE":
            self.draw_gameplay()
            self.renderer.draw_text("PAUSA", 350, 250, (255, 255, 255), 40)

        elif self.state == "GAME_OVER":
            self.renderer.draw_text("GAME OVER", 300, 260, (255, 0, 0), 40)
            self.renderer.draw_text("ENTER para volver", 260, 320, (255, 255, 255), 24)

        elif self.state == "VICTORY":
            self.renderer.draw_text("VICTORIA!", 310, 260, (255, 255, 0), 40)

        # ESCALADO
        window_w, window_h = self.screen.get_size()
        game_w, game_h = self.game_surface.get_size()

        # Deja un margen para que se vea el borde de ventana y la X
        max_scale = 0.7
        scale = min(window_w / game_w, window_h / game_h, max_scale)

        scaled_surface = pygame.transform.smoothscale(
            self.game_surface, (int(game_w * scale), int(game_h * scale))
        )

        x = (window_w - scaled_surface.get_width()) // 2
        y = (window_h - scaled_surface.get_height()) // 2

        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled_surface, (x, y))
        pygame.display.flip()

    # ================================================================
    # GAMEPLAY DRAW
    # ================================================================
    def draw_gameplay(self):
        self.level.draw(self.renderer)
        self.pacman.draw(self.renderer)

        for ghost in self.ghosts:
            ghost.draw(self.renderer)

        self.hud.draw(self.renderer)

    # ================================================================
    # MENU DRAW (capa imperativa)
    # ================================================================
    def draw_menu(self):
        self.menu.draw(self.renderer)
        if self.menu_overlay:
            self.draw_menu_overlay()

    def draw_menu_overlay(self):
        # Panel semitransparente centrado
        panel_width = 500
        panel_height = 260
        x = (self.game_surface.get_width() - panel_width) // 2
        y = 180
        surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 180))
        self.game_surface.blit(surface, (x, y))

        title = self.menu_overlay.get("title", "")
        lines = self.menu_overlay.get("lines", [])

        # Títulos y líneas centradas
        self.renderer.draw_text(title, x + 40, y + 20, (255, 255, 0), 28)
        for i, line in enumerate(lines):
            self.renderer.draw_text(line, x + 40, y + 70 + i * 28, (255, 255, 255), 22)

    # ================================================================
    # VIDA PERDIDA
    # ================================================================
    def handle_pacman_hit(self):
        self.hud.lives -= 1

        # reproducir sonido de muerte ya fue llamado antes
        if self.hud.lives <= 0:
            self.state = "GAME_OVER"
            return

        # asegurar que suene un poco el "death" antes de respawnear
        pygame.time.delay(700)
        self.respawn_entities()

    # ================================================================
    # RESPAWN
    # ================================================================
    def respawn_entities(self):
        spawn_col, spawn_row = self.level.pacman_spawn
        self.pacman.x = spawn_col * TILE_SIZE + TILE_SIZE // 2
        self.pacman.y = spawn_row * TILE_SIZE + TILE_SIZE // 2

        self.pacman.dir_x = 0
        self.pacman.dir_y = 0
        self.pacman.next_dir_x = 0
        self.pacman.next_dir_y = 0

        self.ghosts.clear()

        speed = ghost_speed_for_level(self.difficulty, self.current_level)
        self.spawn_ghosts_for_level(speed=speed)

    # ================================================================
    # RESET GAME
    # ================================================================
    def reset_game(self):
        self.hud.reset()

        self.ghosts.clear()

        self.level = Level("levels/maps/level1.json", game=self)
        self.pacman.level = self.level

        self.respawn_entities()

    # ================================================================
    # POWER-UPS
    # ================================================================
    def freeze_ghosts(self, state):
        for ghost in self.ghosts:
            ghost.frozen = state

    def activate_powerup(self, pacman, col, row):
        p = random.choice([
            SpeedBoost(),
            TimeFreeze(),
            ScoreMultiplier(),
            FrightMode()
        ])

        # Sonido + loop frightened
        self.sfx.play_power()

        pacman.add_effect(p)

    # ================================================================
    # START NORMAL MODE
    # ================================================================
    def start_normal_mode(self):
        self.start_game_with_difficulty("NORMAL")

    def start_menu_selection(self):
        """Imperative shell: lee selección y delega en núcleo funcional."""
        action = self.menu.get_selected_action()
        if action == "start":
            self.start_game_with_difficulty("NORMAL")
        elif action == "exit":
            self._running = False
        elif action == "help":
            self.set_menu_overlay(
                "Ayuda",
                [
                    "Flechas para moverse",
                    "ENTER: seleccionar / iniciar",
                    "P: Pausa en juego",
                    "ESC: cerrar",
                ],
            )
        elif action == "credits":
            self.set_menu_overlay(
                "Creditos",
                [
                    "Equipo:",
                    "ISMAEL",
                    "AMY",
                    "JEAN CARLOS",
                    "STEVEN",
                ],
            )
        elif action == "config":
            self.set_menu_overlay(
                "Configuracion",
                [
                    "Dificultad fija: NORMAL",
                    "Sonido: activado",
                    "Volumen: 60%",
                    "Pulsa ENTER para cerrar",
                ],
            )

    def start_game_with_difficulty(self, name):
        self.difficulty = resolve_difficulty(DIFFICULTY_PRESETS, name)
        self.current_level = 1
        self.reset_game()
        self.state = "GAME"
        self.sfx.play_intro()

    def set_menu_overlay(self, title, lines):
        self.menu_overlay = {"title": title, "lines": lines}

    # ================================================================
    # SIGUIENTE NIVEL
    # ================================================================
    def load_next_level(self):
        self.ghosts.clear()

        self.level = Level("levels/maps/level1.json", game=self)
        self.pacman.level = self.level

        self.respawn_entities()

    # ================================================================
    # UTIL: EXPOSE SOUND HELPERS PARA LLAMAR DESDE OTROS MÓDULOS
    # ================================================================
    def play_waka(self):
        """Llamar desde pacman/level cuando se come un pellet."""
        self.sfx.play_waka()

    def play_tunnel(self):
        self.sfx.play_tunnel()

    def stop_frightened_sound(self):
        self.sfx.stop_frightened()

    def play_fruit_sound(self):
        self.sfx.play_fruit()

    def play_ghost_exit_sound(self):
        self.sfx.play_ghost_exit()

    def play_step_sound(self):
        """Puedes llamar esto manualmente desde pacman si prefieres; internamente ya detecta movimiento."""
        self.sfx.play_step()
