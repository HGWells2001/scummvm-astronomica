"""Original Astronomica cursors must use the player's GAMEPLAC bitmap pairs.

The source files are verified without bundling proprietary cursor pixels.
Windows CI compiles the actual C++ implementation.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "outputs" / "astronomica-cleanroom" / "engine" / "astronomica"

class OriginalCursorIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = (ENGINE / "original_cursors.cpp").read_text(encoding="utf-8")
        cls.h = (ENGINE / "original_cursors.h").read_text(encoding="utf-8")
        cls.engine = (ENGINE / "astronomica.cpp").read_text(encoding="utf-8")
        cls.module = (ENGINE / "module.mk").read_text(encoding="utf-8")

    def test_loads_original_gameplac_pairs_not_executable_resources(self):
        self.assertIn('PLACES/GAMEPLAC/%s_S', self.c)
        self.assertIn('PLACES/GAMEPLAC/%s_M', self.c)
        self.assertIn('readMonochromeBMP(shapePath, shape)', self.c)
        self.assertIn('readMonochromeBMP(maskPath, mask)', self.c)
        self.assertNotIn('ASTROeng.EXE', self.c)
        self.assertNotIn('createFromEXE', self.c)

    def test_decodes_one_bit_bottom_up_bitmaps_and_masks(self):
        self.assertIn('bits != 1', self.c)
        self.assertIn('compression != 0', self.c)
        self.assertIn('height != kCursorSize', self.c)
        self.assertIn('pixelOffset < 62', self.c)
        self.assertIn('kCursorSize - bottomRow - 1', self.c)
        self.assertIn('mask[i] ? (shape[i] ? 1 : 2) : 0', self.c)
        self.assertIn('getKeyColor() const override { return 0; }', self.c)
        self.assertIn('getPaletteStartIndex() const override { return 1; }', self.c)

    def test_uses_gamedef_order_and_original_hotspots(self):
        for definition in (
            '{"HAND",  1,  8,  2}',
            '{"LEFT",  2,  1,  8}',
            '{"UP",    3,  8,  2}',
            '{"RIGHT", 4, 15,  8}',
            '{"DOWN",  5,  8, 15}',
            '{"ARROW", 0,  0,  0}',
        ):
            self.assertIn(definition, self.c)

    def test_scene_driven_cursor_selection_not_guessed(self):
        self.assertIn('cursorID = s.cursor;', self.engine)
        self.assertIn('_originalCursors.contains(uint32(s.cursor))', self.engine)
        self.assertIn('pointInSprite(s,bmp->w,bmp->h,x,y)', self.engine)
        self.assertIn('updateOriginalCursor(mouse.x,mouse.y);', self.engine)
        self.assertIn('_cursorPointPlace = -1;', self.engine)

    def test_fallback_and_engine_module(self):
        self.assertIn('CursorMan.setDefaultArrowCursor()', self.c)
        self.assertIn('if (!cursor) cursor = _defaultArrow;', self.c)
        self.assertIn('CursorMan.replaceCursor(cursor)', self.c)
        self.assertIn('ConfMan.hasKey("astronomica_original_cursors")', self.engine)
        self.assertIn('original_cursors.o', self.module)
        self.assertIn('#include "astronomica/original_cursors.h"',
                      (ENGINE / "astronomica.h").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
