import unittest

from core.functional_core import ghost_speed_for_level, resolve_difficulty
from ui.menu import cycle_option, reduce_menu_selection


class MenuReducerTest(unittest.TestCase):
    def test_cycle_option_wraps_indexes(self):
        self.assertEqual(cycle_option(0, -1, 4), 3)
        self.assertEqual(cycle_option(3, 1, 4), 0)

    def test_reduce_menu_selection_keeps_purity(self):
        options = ["EASY", "NORMAL", "HARD"]
        self.assertEqual(reduce_menu_selection(0, "DOWN", options), 1)
        self.assertEqual(reduce_menu_selection(2, "UP", options), 1)
        self.assertEqual(reduce_menu_selection(1, "NONE", options), 1)


class DifficultyHelpersTest(unittest.TestCase):
    def test_resolve_difficulty_defaults(self):
        presets = {"NORMAL": {"ghost_speed": 120, "ghost_speed_growth": 1.0}}
        selected = resolve_difficulty(presets, "UNKNOWN")
        self.assertEqual(selected, presets["NORMAL"])

    def test_ghost_speed_for_level_scales(self):
        preset = {"ghost_speed": 100, "ghost_speed_growth": 1.2}
        self.assertAlmostEqual(ghost_speed_for_level(preset, 1), 100)
        self.assertAlmostEqual(ghost_speed_for_level(preset, 3), 100 * (1.2 ** 2))
        # Nivel se trunca a 1 para evitar velocidades negativas
        self.assertAlmostEqual(ghost_speed_for_level(preset, 0), 100)


if __name__ == "__main__":
    unittest.main()
