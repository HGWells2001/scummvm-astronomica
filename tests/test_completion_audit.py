"""Pure unit tests; do not require copyrighted game data."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from completion_audit import index_scenes, decode_scene, _commands, MUST_HAVE


class TestCompletionAudit(unittest.TestCase):
    def test_directories_not_confused_with_scenes(self):
        actual, duplicates = index_scenes(["PLACES/P1/", "PLACES/P1/S0.WAV",
                                           "PLACES/P1/MEGAFILE.HYP", "PLACES/P537/MEGAFILE.HYP"])
        self.assertEqual(set(actual), {1, 537})
        self.assertFalse(duplicates)

    def test_duplicate_scene_ids_refused(self):
        _, duplicates = index_scenes(["PLACES/P1/MEGAFILE.HYP", "places/p01/megafile.hyp"])
        self.assertEqual(len(duplicates), 1)

    def test_required_ending_and_puzzles(self):
        self.assertTrue(set(range(501, 538)).issubset(MUST_HAVE))
        self.assertTrue({0, 1, 423, 424, 425, 432, 433, 435, 436, 437}.issubset(MUST_HAVE))

    def test_recognize_commands_without_images_or_duplicates(self):
        scene = {"sprites": [{"click": [{"opcode": 5, "args": [537]}]}],
                 "other": {"data": [7, 8]},
                 "script": [{"opcode": 23, "args": [26, 5, 0, 0, 0, 0]}]}
        self.assertEqual([c["opcode"] for c in _commands(scene)], [5, 23])

    def test_trailing_original_bytes_are_not_a_parser_failure(self):
        class FormatError(ValueError):
            pass
        parser = Mock()
        parser.FormatError = FormatError
        def parse(content):
            if len(content) == 10:
                raise FormatError("trailing 4 bytes at 0x6")
            self.assertEqual(content, b"012345")
            return {"mode": 1}
        parser.parse.side_effect = parse
        scene, trailing = decode_scene(parser, b"0123456789")
        self.assertEqual(scene["mode"], 1)
        self.assertEqual(trailing, 4)

    def test_arbitrary_parse_failure_is_not_suppressed(self):
        class FormatError(ValueError):
            pass
        parser = Mock()
        parser.FormatError = FormatError
        parser.parse.side_effect = FormatError("invalid BMP at 0x7")
        with self.assertRaises(FormatError):
            decode_scene(parser, b"abcdef")


if __name__ == "__main__":
    unittest.main()
