from pathlib import Path
import shutil
r=Path('outputs/astronomica-cleanroom/engine/astronomica')
p=r/'resource.h';s=p.read_text().replace(' int16 renderX', ' bool clickEnabled = false, dragEnabled = false, autoFrame = false, autoMove = false;\n int16 renderX');p.write_text(s)
p=r/'resource.cpp';s=p.read_text().replace(' if (flag()) { sp.clickType', ' sp.clickEnabled = flag();\n if (sp.clickEnabled) { sp.clickType').replace(' if (flag()) sp.drag = script();',' sp.dragEnabled = flag();\n if (sp.dragEnabled) sp.drag = script();').replace(' if (flag()) numbers(sp.frameData, 3);', ' sp.autoFrame = flag();\n if (sp.autoFrame) numbers(sp.frameData, 3);').replace(' if (flag()) numbers(sp.moveData, 5);',' sp.autoMove = flag();\n if (sp.autoMove) numbers(sp.moveData, 5);');p.write_text(s)
p=r/'sprites.h';s=p.read_text().replace('uint spriteFrameCount', 'bool pointInSprite(const Sprite &sprite, int width, int height, int x, int y);\nconst Frame *spriteFrameAt(const Scene &scene, uint index, uint frame);\nuint spriteFrameCount');p.write_text(s)
p=r/'sprites.cpp';s=p.read_text().replace('uint spriteFrameCount', '''bool pointInSprite(const Sprite &sprite, int width, int height, int x, int y) {
 // 7:0ec1 uses signed 16-bit, inclusive comparisons on all four edges.
 const int16 right = int16(int32(sprite.renderX) + width);
 const int16 bottom = int16(int32(sprite.renderY) + height);
 return int16(x) >= sprite.renderX && int16(x) <= right && int16(y) >= sprite.renderY && int16(y) <= bottom;
}
const Frame *spriteFrameAt(const Scene &scene, uint index, uint frame) {
 const int owner = frameOwner(scene, index);
 if (owner < 0 || frame >= scene.sprites[owner].frames.size()) return nullptr;
 return &scene.sprites[owner].frames[frame];
}
uint spriteFrameCount''',1)
s=s.replace(' Scene chain; Sprite source;', ''' Sprite hit; hit.renderX = 10; hit.renderY = 20; hit.visible = 0;
 if (!pointInSprite(hit, 4, 5, 10, 20) || !pointInSprite(hit, 4, 5, 14, 25) || pointInSprite(hit, 4, 5, 15, 25) || pointInSprite(hit, 4, 5, 14, 26) || pointInSprite(hit, 4, 5, 9, 20)) return false;
 hit.renderX = 32767;
 if (pointInSprite(hit, 4, 5, 32767, 20)) return false;
 Scene chain; Sprite source;''');p.write_text(s)
p=r/'script.h';s=p.read_text().replace('_lastTrue(false), _executed(0)', '_lastTrue(false), _clicksBlocked(false), _executed(0)').replace(' bool _lastTrue;', ' bool _lastTrue;\n bool _clicksBlocked;').replace(' uint executedCount()', ' bool clicksBlocked() const { return _clicksBlocked; }\n uint executedCount()');p.write_text(s)
p=r/'script.cpp';s=p.read_text().replace(' _programs.clear();',' _programs.clear();\n _clicksBlocked = false; // _do_place 9:01e0 resets the global input lock.')
s=s.replace('  case 41:', '  case 28: case 29:\n   if (c.args.size() != 1 || c.args[0] >= 0) return false;\n   break;\n  case 41:',1)
s=s.replace('  } else if (c.opcode == 41) {', '  } else if (c.opcode == 28 || c.opcode == 29) {\n   _clicksBlocked = c.opcode == 28;\n  } else if (c.opcode == 41) {')
p.write_text(s)
p=r/'astronomica.h';s=p.read_text().replace(' void clickAt(int x, int y);',' int spriteAt(int x, int y);\n void clickAt(int x, int y);');p.write_text(s)
p=r/'astronomica.cpp';s=p.read_text()
start=s.index('void AstronomicaEngine::clickAt(int x, int y) {');end=s.index(' for (uint i = 0; i < _scene.mouseRects.size(); ++i)',start)
s=s[:start]+'''int AstronomicaEngine::spriteAt(int x, int y) {
 Common::File file;
 const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d/MEGAFILE.HYP", _place)));
 if (!file.open(Common::FSNode(path))) return -2;
 for (uint i = 0; i < _scene.sprites.size(); ++i) {
  const Sprite &s = _scene.sprites[i];
  if (!s.clickEnabled && !s.dragEnabled) continue;
  // Until their changing geometry is reconstructed, do not guess a hit.
  if (_scene.layers != 1 || s.layer != 1 || s.autoMove || s.autoFrame) return -2;
  const uint count = spriteFrameCount(_scene, i);
  if (!count) return -2;
  int width = -1, height = -1;
  // With no selected preview frame, accept only invariant frame dimensions.
  for (uint f = 0; f < count; ++f) {
   if (s.selectedFrame >= 0 && uint(s.selectedFrame) != f) continue;
   const Frame *frame = spriteFrameAt(_scene, i, f);
   Graphics::Surface *bmp = frame ? decodeSpriteBitmap(file, frame->image, _screen.format) : nullptr;
   if (!bmp) return -2;
   const bool mismatch = width >= 0 && (width != bmp->w || height != bmp->h);
   width = bmp->w; height = bmp->h; bmp->free(); delete bmp;
   if (mismatch) return -2;
  }
  if (width < 0) return -2;
  // Original hit test ignores visibility and mask pixels.
  if (pointInSprite(s, width, height, x, y)) return int(i);
 }
 return -1;
}
void AstronomicaEngine::clickAt(int x, int y) {
 if (_runner.clicksBlocked()) return;
 if (!_scene.sprites.empty()) {
  if (!ConfMan.hasKey("astronomica_sprite_input") || !ConfMan.getBool("astronomica_sprite_input")) return;
  const int hit = spriteAt(x, y);
  if (hit == -2) { warning("Astronomica: sprite input geometry incomplete in P%d", _place); return; }
  if (hit >= 0) {
   const Sprite &s = _scene.sprites[hit];
   // clickType 2 invokes additional drag setup; only type 0 is enabled.
   if (!s.clickEnabled || s.dragEnabled || s.clickType != 0 || !_runner.enqueue(s.click, scriptClock(), true))
    warning("Astronomica: unsupported sprite click in P%d, sprite %d", _place, hit + 1);
   return; // A sprite always consumes the hit, even if its script is rejected.
  }
 }
'''+s[end:]
# Test original complete P510 radio-button click, no command extraction.
anchor='  // Full, unmodified P29 entry program:'
test='''  ConfMan.setBool("astronomica_sprite_input", true);
  bool mouseOK = loadPlace(510) && spriteAt(227,384) == 9 && spriteAt(256,411) == 9;
  mouseOK = spriteAt(257,411) != 9 && spriteAt(226,384) != 9 && mouseOK;
  const uint beforeClick = _runner.executedCount();
  clickAt(227,384);
  mouseOK = _runner.pendingCount() == 1 && _runner.executedCount() == beforeClick && mouseOK;
  runScriptsAt(0); // lock, then queue the frame changes
  const uint pendingLocked = _runner.pendingCount();
  clickAt(253,363);
  mouseOK = _runner.clicksBlocked() && _runner.pendingCount() == pendingLocked && mouseOK;
  runScriptsAt(0); runScriptsAt(0); // frames, then local state
  int32 button = 0;
  mouseOK = _scene.sprites[9].selectedFrame == 1 && _runner.getValue(1,4,button) && button == 1 && mouseOK;
  for (uint i = 10; i < 14; ++i) mouseOK = _scene.sprites[i].selectedFrame == 0 && mouseOK;
  mouseOK = screenRGBHash(_screen) == (rgb565 ? 0x518eade8U : 0xf9c9f648U) && mouseOK;
  runScriptsAt(149); mouseOK = _runner.clicksBlocked() && mouseOK;
  runScriptsAt(150); mouseOK = !_runner.clicksBlocked() && !_runner.pendingCount() && mouseOK;
  clickAt(253,363); runScriptsAt(0); runScriptsAt(0); runScriptsAt(0);
  mouseOK = _scene.sprites[9].selectedFrame == 0 && _scene.sprites[10].selectedFrame == 1 && _runner.getValue(1,4,button) && button == 2 && mouseOK;
  mouseOK = loadPlace(103) && !_runner.clicksBlocked() && !_runner.pendingCount() && mouseOK;
  ConfMan.setBool("astronomica_sprite_input", false);
  debug("Astronomica mouse verification: %s (P510 original button scripts, inclusive bounds, 149/150 ms lock, scene reset)", mouseOK ? "PASS" : "FAIL");
  scriptsOK = mouseOK && scriptsOK;
'''
s=s.replace(anchor,test+anchor);p.write_text(s)
for p in r.iterdir(): shutil.copy2(p,Path('work/fresh-20260913/scummvm/engines/astronomica')/p.name)
