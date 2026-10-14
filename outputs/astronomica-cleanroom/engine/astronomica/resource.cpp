// SPDX-License-Identifier: GPL-3.0-or-later
// Field order recovered from ASTRO.EXE 9:1404 and 9:2ff2; see FORMAT.md.
#include "astronomica/resource.h"
namespace Astronomica {
int32 ResourceReader::number() {
 if (!_ok || _s.size() - _s.pos() < 4) { _ok = false; return 0; }
 return _s.readSint32LE();
}
uint32 ResourceReader::count() {
 const int32 value = number();
 if (value < 0 || value > 10000) { _ok = false; return 0; }
 return value;
}
bool ResourceReader::flag() {
 const int32 value = number();
 if (value != 0 && value != 1) _ok = false;
 return value == 1 && _ok;
}
void ResourceReader::numbers(int32 *v, uint n) { for (uint i = 0; i < n; ++i) v[i] = number(); }
Common::String ResourceReader::text() {
 if (!_ok || _s.size() - _s.pos() < 255) { _ok = false; return Common::String(); }
 char buffer[256];
 if (_s.read(buffer, 255) != 255) _ok = false;
 buffer[255] = 0;
 return Common::String(buffer);
}
BitmapRef ResourceReader::bitmap() {
 BitmapRef ref;
 const int32 size = number();
 if (!_ok || size < 54 || size > _s.size() - _s.pos()) { _ok = false; return ref; }
 ref.offset = _s.pos(); ref.size = size;
 if (_s.readUint16LE() != 0x4d42 || _s.readUint32LE() != ref.size) { _ok = false; return ref; }
 if (!_s.seek(ref.offset + ref.size)) _ok = false;
 ++_bitmaps;
 return ref;
}
BitmapRef ResourceReader::image() {
 if (!flag()) return BitmapRef();
 if (flag()) return bitmap();
 text(); // External image names are parsed but not rendered by this prototype.
 return BitmapRef();
}
// Number of int32 arguments, excluding the shared delay. -1 is invalid.
static int argumentCount(int32 op) {
 switch (op) {
 case 1: case 2: case 6: case 8: case 11: case 12: case 13: case 14:
 case 21: case 25: case 26: case 35: case 42: case 43: case 44: case 45:
 case 49: case 50: case 51: return 0;
 case 4: case 5: case 9: case 10: case 16: case 17: case 27: case 28:
 case 29: case 30: case 41: return 1;
 case 15: case 20: case 36: case 38: return 2;
 case 7: case 32: case 37: case 46: case 47: case 48: return 3;
 case 3: case 19: case 24: case 33: case 39: case 40: return 4;
 case 18: case 23: case 31: return 6;
 default: return -1;
 }
}
Script ResourceReader::script() {
 Script result;
 while (_ok) {
  Command cmd; cmd.offset = _s.pos(); cmd.opcode = number();
  if (!cmd.opcode) break;
  const int n = argumentCount(cmd.opcode);
  if (n < 0 || ++_commands > 100000) { _ok = false; break; }
  if (cmd.opcode == 20 || cmd.opcode == 50) cmd.text = text();
  for (int i = 0; i < n; ++i) cmd.args.push_back(number());
  cmd.delay = number(); result.push_back(cmd);
 }
 return result;
}
Script ResourceReader::optionalScript() { return flag() ? script() : Script(); }
Sprite ResourceReader::sprite() {
 Sprite sp; sp.clone = number();
 if (sp.clone == -1) {
  const uint32 n = count();
  for (uint32 i = 0; _ok && i < n; ++i) { Frame f; f.image = bitmap(); f.mask = bitmap(); sp.frames.push_back(f); }
 }
   sp.layer = number(); sp.visible = flag(); sp.x = number(); sp.y = number();
   sp.renderX = int16(sp.x); sp.renderY = int16(sp.y);
 sp.clickEnabled = flag();
 if (sp.clickEnabled) { sp.clickType = number(); sp.click = script(); }
 sp.dragEnabled = flag();
 if (sp.dragEnabled) sp.drag = script();
 numbers(sp.rect, 4); sp.mouseIn = optionalScript(); sp.mouseOut = optionalScript();
 sp.autoFrame = flag();
 if (sp.autoFrame) numbers(sp.frameData, 3);
 sp.autoMove = flag();
 if (sp.autoMove) numbers(sp.moveData, 5);
 if (flag()) sp.cursor = number();
 return sp;
}
bool ResourceReader::read(Scene &scene) {
 scene.mode = number();
 if (scene.mode != 0 && scene.mode != 1 && scene.mode != 3) _ok = false;
 if (scene.mode == 1) numbers(scene.nav, 3);
 scene.background = image(); scene.control = image();
 scene.introSound = flag();
 if (scene.introSound) scene.introSoundId = number();
 scene.layers = count();
 const uint32 spriteCount = count(), soundCount = count(), movieCount = count();
 count(); text();
 for (uint32 i = 0; _ok && i < spriteCount; ++i) scene.sprites.push_back(sprite());
 for (uint32 i = 0; _ok && i < soundCount; ++i) { number(); number(); }
 for (uint32 i = 0; _ok && i < movieCount; ++i) scene.movies.push_back(text());
 uint32 n = count();
 for (uint32 i = 0; _ok && i < n; ++i) scene.scripts.push_back(script());
 n = count();
 for (uint32 i = 0; _ok && i < n; ++i) {
  MouseRect rect; numbers(rect.rect, 4);
  rect.click = optionalScript(); rect.mouseIn = optionalScript(); rect.mouseOut = optionalScript();
  scene.mouseRects.push_back(rect);
 }
 n = count();
 for (uint32 i = 0; _ok && i < n; ++i) { Condition c; numbers(c.raw, 6); scene.conditions.push_back(c); }
 scene.consumed = _s.pos(); scene.trailing = _s.size() - _s.pos();
 scene.bitmapCount = _bitmaps; scene.commandCount = _commands;
 return _ok && !_s.err();
}
}
