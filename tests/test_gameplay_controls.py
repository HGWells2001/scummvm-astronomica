"""Protect normal progression from developer shortcuts.

Static source-contract tests. A real Windows build and actual user
playthrough are required for full behavioral acceptance.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "outputs" / "astronomica-cleanroom" / "engine" / "astronomica" / "astronomica.cpp"
LAUNCHER = ROOT / "Avvia-Astronomica.cmd"


class TestNormalGameplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = ENGINE.read_text(encoding="utf-8")
        cls.loop = cls.code[cls.code.rfind(" while (!shouldQuit()) {"):]
        cls.launcher = LAUNCHER.read_text(encoding="utf-8")

    def test_page_navigation_requires_explicit_developer_switch(self):
        self.assertIn(
            'ConfMan.hasKey("astronomica_debug_controls") && ConfMan.getBool("astronomica_debug_controls")',
            self.code
        )
        self.assertIn("case Common::KEYCODE_PAGEDOWN: if (developerControls) stepPlace(1);", self.loop)
        self.assertIn("case Common::KEYCODE_PAGEUP: if (developerControls) stepPlace(-1);", self.loop)
        self.assertNotIn("case Common::KEYCODE_PAGEDOWN: stepPlace(1);", self.loop)
        self.assertNotIn("case Common::KEYCODE_PAGEUP: stepPlace(-1);", self.loop)

    def test_demo_keys_are_developer_only(self):
        for key in "vrcf":
            start = self.loop.index("case Common::KEYCODE_" + key + ":")
            self.assertIn("developerControls", self.loop[start:start+180], key)
        self.assertIn("if (developerControls && _place == 517", self.loop)
        self.assertIn("else if (developerControls && _place == 510)", self.loop)

    def test_game_controls_still_available(self):
        self.assertIn("case Common::KEYCODE_F5: openMainMenuDialog();", self.loop)
        self.assertIn("case Common::KEYCODE_ESCAPE: quitGame();", self.loop)
        self.assertIn("case Common::KEYCODE_LEFT: if (_nav[0] > 0)", self.loop)

    def test_route_trace_is_opt_in_and_logs_no_original_media(self):
        self.assertIn('ConfMan.getBool("astronomica_trace_route")', self.code)
        for marker in ["Astronomica route startup:", "Astronomica route click:",
                       "Astronomica route request:", "Astronomica route accepted:",
                       "Astronomica route LOAD FAILURE:"]:
            self.assertIn(marker, self.code)
        self.assertIn('if /i "%ASTRO_TRACE%"=="1"', self.launcher)
        self.assertIn('set "ASTRO_TRACE_ARGS=--debuglevel=1"', self.launcher)


if __name__ == "__main__":
    unittest.main()
