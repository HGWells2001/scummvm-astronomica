"""Native regression harness safety/behavior checks (no copyrighted assets)."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, SimpleNamespace
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from verify_gameplay import CHECKS, make_config, plan, scan_verdict, execute

class TestGameplayRunner(unittest.TestCase):
    def test_all_suites_are_ordered_and_unique(self):
        total = plan("all")
        self.assertEqual(len(total), sum(len(v) for v in CHECKS.values()))
        self.assertEqual(len({key for key, marker in total}), len(total))
        self.assertTrue(all(key.startswith("astronomica_verify") for key, marker in total))
        self.assertTrue(all(marker.startswith("Astronomica ") for key, marker in total))

    def test_config_has_only_one_test_flag_and_uses_original_path(self):
        cfg = make_config(Path("C:/Games/Astronomica"), "astronomica_verify_endings")
        self.assertIn("path=C:/Games/Astronomica", cfg)
        self.assertIn("astronomica_verify_endings=true", cfg)
        self.assertIn("[astronomica-audit]", cfg)
        self.assertNotIn("savepath=", cfg)

    def test_config_rejects_unrecognized_flags(self):
        with self.assertRaises(ValueError):
            make_config(Path("game_data"), "astronomica_verify_typo")

    def test_verdict_needs_marker_and_zero_exit(self):
        marker = "Astronomica post-credits verification: PASS"
        self.assertTrue(scan_verdict(0, "DEBUG: " + marker, marker))
        self.assertFalse(scan_verdict(1, marker, marker))
        self.assertFalse(scan_verdict(0, "Astronomica post-credits verification: FAIL", marker))
        self.assertFalse(scan_verdict(0, "No tests were run", marker))

    def test_reports_and_isolates_native_files(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            game = root / "game"
            (game / "PLACES").mkdir(parents=True)
            (game / "PLACES" / "GAMEDATA").write_bytes(b"mock")
            exe = root / "scummvm.exe"
            exe.write_bytes(b"fixture")
            report_path = root / "evidence"
            expected = CHECKS["core"][0][1]
            def fake_run(args, **kwargs):
                if "--list-engines" in args:
                    return SimpleNamespace(returncode=0, stdout="astronomica  Astronomica / Hyper-Trieve", stderr="")
                return SimpleNamespace(returncode=0, stdout=expected, stderr="")
            with patch("verify_gameplay.subprocess.run", side_effect=fake_run):
                # Run only the one-check fixture, not every core check.
                with patch("verify_gameplay.plan", return_value=CHECKS["core"][:1]):
                    report = execute(exe, game, report_path, "core", 60)
            self.assertTrue(report["passed"])
            self.assertEqual(len(report["checks"]), 1)
            self.assertTrue((report_path / "summary.json").exists())
            self.assertTrue((report_path / CHECKS["core"][0][0] / "isolated-saves").is_dir())
            with self.assertRaises(FileExistsError):
                with patch("verify_gameplay.subprocess.run", side_effect=fake_run):
                    execute(exe, game, report_path, "core", 60)

    def test_unknown_registered_engine_blocks_checks(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            game = root / "game"
            (game / "PLACES").mkdir(parents=True)
            (game / "PLACES" / "GAMEDATA").write_bytes(b"mock")
            exe = root / "scummvm.exe"
            exe.write_bytes(b"fixture")
            with patch("verify_gameplay.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout="scumm", stderr="")):
                with self.assertRaises(RuntimeError):
                    execute(exe, game, root / "report", "core", 60)
            self.assertTrue((root / "report" / "summary.json").is_file())

if __name__ == "__main__":
    unittest.main()
