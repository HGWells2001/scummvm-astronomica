from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica/script.cpp');s=p.read_text();start=s.index('  case 20:\n');end=s.index('  case 23:\n',start);s=s[:start]+'''  case 20:
   if (c.args.size() != 2 || c.text.empty()) return false;
   break;
  case 49:
   if (!c.args.empty()) return false;
   break;
'''+s[end:];s=s.replace('if (c.opcode == 25 ||', 'if (c.opcode == 49 || c.opcode == 25 ||');p.write_text(s)
p=p.with_name('astronomica.h');s=p.read_text().replace('~AstronomicaEngine() override {', '~AstronomicaEngine() override { _pendingImage.free();');s=s.replace(' bool drawBackgroundImage(const Common::String &name, int x, int y);',' bool stageBackgroundImage(const Common::String &name, int x, int y);\n void displayBackgroundImage();\n Graphics::Surface _pendingImage;\n int _pendingImageX = 0, _pendingImageY = 0;');p.write_text(s)
p=p.with_name('astronomica.cpp');s=p.read_text().replace(' _loopSound = -1; _loopEnabled = true;', ' _pendingImage.free();\n _loopSound = -1; _loopEnabled = true;');start=s.index('bool AstronomicaEngine::drawBackgroundImage');end=s.index('void AstronomicaEngine::configureSounds()',start);s=s[:start]+'''bool AstronomicaEngine::stageBackgroundImage(const Common::String &name, int x, int y) {
 Graphics::Surface *src = openBackgroundImage(name);
 if (!src) return false;
 _pendingImage.copyFrom(*src); _pendingImageX = x; _pendingImageY = y;
 src->free(); delete src; return true;
}
void AstronomicaEngine::displayBackgroundImage() {
 // The loaded image is shared by script invocations until display or reload.
 for (int sy = 0; sy < _pendingImage.h; ++sy) for (int sx = 0; sx < _pendingImage.w; ++sx) {
  const int x = _pendingImageX+sx, y = _pendingImageY+sy;
  if (x >= 0 && x < _background.w && y >= 0 && y < _background.h)
   _background.setPixel(x,y,_pendingImage.getPixel(sx,sy));
 }
 // Original deletes the bitmap after copying. Do not retain a stale handle.
 _pendingImage.free(); redrawSprites();
}
'''+s[end:];s=s.replace('if (drawBackgroundImage(action.text,action.x,action.y)) { redrawSprites(); dirty = false; }','if (stageBackgroundImage(action.text,action.x,action.y)) {}');s=s.replace('  if (action.opcode == 25) {','  if (action.opcode == 49) { displayBackgroundImage(); dirty = false; continue; }\n  if (action.opcode == 25) {');s=s.replace('if (stageBackgroundImage(action.text,action.x,action.y)) {}\n   else warning','if (!stageBackgroundImage(action.text,action.x,action.y)) warning');s=s.replace('imageOK = !_runner.start(delayedDisplay,0,true) && imageOK;', 'imageOK = _runner.start(delayedDisplay,0,true) && imageOK; applyScriptActions(0);\n    runScriptsAt(0); imageOK = _pendingImage.w > 0 && imageOK;\n    runScriptsAt(1); imageOK = _pendingImage.w == 0 && screenRGBHash(_screen) == expected && imageOK;');s=s.replace('// P508 stages its bitmap across branch control; this form remains rejected.', '// P508 stages its bitmap across branch control; this form is now admitted.').replace('loadPlace(508) && !_runner.canRun(_scene.scripts[1],true)', 'loadPlace(508) && _runner.canRun(_scene.scripts[1],true)');p.write_text(s)
