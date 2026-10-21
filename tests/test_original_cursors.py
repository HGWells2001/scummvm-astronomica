"""Verify cursor integration never substitutes invented game artwork.

Static contract tests; the Windows executable is still compiled separately
and authentic cursor pixels can only be verified against the user's CD.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"outputs"/"astronomica-cleanroom"/"engine"/"astronomica"

class OriginalCursorIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=(ENGINE/"original_cursors.cpp").read_text(encoding="utf-8")
        cls.h=(ENGINE/"original_cursors.h").read_text(encoding="utf-8")
        cls.engine=(ENGINE/"astronomica.cpp").read_text(encoding="utf-8")
        cls.module=(ENGINE/"module.mk").read_text(encoding="utf-8")

    def test_cursors_are_taken_from_original_english_exe(self):
        self.assertIn('"SETUP/ASTROeng.EXE"',self.c)
        self.assertIn('"SETUP/ASTRO.EXE"',self.c)
        self.assertIn('Common::WinResources::createFromEXE',self.c)
        self.assertIn('Common::kWinGroupCursor',self.c)
        self.assertIn('Common::kWinCursor',self.c)
        self.assertIn('Graphics::loadWindowsCursorFromDIB',self.c)

    def test_uses_original_hotspot_palette_and_transparency(self):
        self.assertIn('Graphics::WinCursorGroup::createCursorGroup',self.c)
        self.assertIn('Graphics::makeDefaultWinCursor()',self.c)
        self.assertIn('CursorMan.replaceCursor(cursor)',self.c)
        self.assertNotIn('static const byte arrow',self.c)

    def test_scene_driven_cursor_selection_not_guessed(self):
        self.assertIn('cursorID = s.cursor;',self.engine)
        self.assertIn('_originalCursors.contains(uint32(s.cursor))',self.engine)
        self.assertIn('pointInSprite(s,bmp->w,bmp->h,x,y)',self.engine)
        self.assertIn('updateOriginalCursor(mouse.x,mouse.y);',self.engine)
        self.assertIn('_cursorPointPlace = -1;',self.engine)

    def test_native_cursor_option_preserves_fallback(self):
        self.assertIn('ConfMan.hasKey("astronomica_original_cursors")',self.engine)
        self.assertIn('ConfMan.getBool("astronomica_original_cursors")',self.engine)
        self.assertIn('if (!exe)',self.c)
        self.assertIn('if (!_loaded || id == _currentID) return;',self.c)
        self.assertIn('if (!cursor) cursor = _windowsArrow;',self.c)
        self.assertIn('if (!_originalCursors.loaded()',self.engine)

    def test_engine_module_links_cursor_source(self):
        self.assertIn('original_cursors.o',self.module)
        self.assertIn('#include "astronomica/original_cursors.h"',
                      (ENGINE/"astronomica.h").read_text(encoding="utf-8"))

if __name__=="__main__":unittest.main()
