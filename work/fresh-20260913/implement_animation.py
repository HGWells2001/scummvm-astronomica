from pathlib import Path
import shutil
r=Path('outputs/astronomica-cleanroom/engine/astronomica')
p=r/'resource.h';s=p.read_text().replace(' int32 selectedFrame', ' uint32 frameSince = 0;\n int32 selectedFrame');p.write_text(s)
p=r/'sprites.h';s=p.read_text().replace('bool pointInSprite', 'bool advanceSpriteFrame(Sprite &sprite, uint frameCount, uint32 now);\nbool pointInSprite');p.write_text(s)
p=r/'sprites.cpp';s=p.read_text().replace('bool pointInSprite', '''bool advanceSpriteFrame(Sprite &sprite, uint frameCount, uint32 now) {
 // _load_place passes the first timing field through signed 16-bit AX.
 const int32 period = int16(sprite.frameData[0]);
 if (!sprite.autoFrame || sprite.autoMove || sprite.clone != -1 || sprite.layer != 1 ||
     sprite.frameData[1] != 1 || sprite.frameData[2] != 0 || period < 0 ||
     !frameCount || sprite.selectedFrame < 0 || uint(sprite.selectedFrame) >= frameCount) return false;
 if (int32(now - sprite.frameSince) < period) return false;
 // Original updates time to now, never catches up multiple missed frames.
 sprite.frameSince = now;
 sprite.selectedFrame = (uint(sprite.selectedFrame) + 1) % frameCount;
 return true;
}
bool pointInSprite''',1)
s=s.replace(' Sprite hit;', ''' Sprite animated; animated.autoFrame = true; animated.layer = 1;
 animated.frameData[0] = 400; animated.frameData[1] = 1; animated.selectedFrame = 0;
 if (advanceSpriteFrame(animated,2,399) || !advanceSpriteFrame(animated,2,400) || animated.selectedFrame != 1) return false;
 if (!advanceSpriteFrame(animated,2,2000) || animated.selectedFrame != 0 || advanceSpriteFrame(animated,2,2399)) return false;
 animated.frameSince = 0xffffff00U;
 if (advanceSpriteFrame(animated,2,143) || !advanceSpriteFrame(animated,2,144)) return false;
 animated.frameData[0] = -1;
 if (advanceSpriteFrame(animated,2,10000)) return false;
 animated.frameData[0] = 0;
 if (!advanceSpriteFrame(animated,2,144) || !advanceSpriteFrame(animated,2,144)) return false;
 Sprite hit;''');p.write_text(s)
p=r/'astronomica.h';s=p.read_text().replace(' void runScriptsAt(uint32 now);', ' void runScriptsAt(uint32 now);\n void animateSpritesAt(uint32 now);');p.write_text(s)
p=r/'astronomica.cpp';s=p.read_text()
s=s.replace(' const uint spritesDrawn = renderStaticSprites(file, parsed, candidate);', ''' if (ConfMan.hasKey("astronomica_animation") && ConfMan.getBool("astronomica_animation") && parsed.layers == 1) {
  // _SWAddFrame selects frames[0]; _CreateSpriteFromBmpMem sets range 0..n-1.
  for (uint i = 0; i < parsed.sprites.size(); ++i) {
   Sprite &s = parsed.sprites[i];
   if (s.clone == -1 && s.layer == 1 && !s.frames.empty()) s.selectedFrame = 0;
  }
 }
 const uint spritesDrawn = renderStaticSprites(file, parsed, candidate);''')
s=s.replace('void AstronomicaEngine::stepPlace(int direction) {', '''void AstronomicaEngine::animateSpritesAt(uint32 now) {
 if (!ConfMan.hasKey("astronomica_animation") || !ConfMan.getBool("astronomica_animation") || _scene.layers != 1) return;
 bool dirty = false;
 for (uint i = 0; i < _scene.sprites.size(); ++i) {
  Sprite &s = _scene.sprites[i];
  if (advanceSpriteFrame(s, spriteFrameCount(_scene,i), now) && s.visible) dirty = true;
 }
 if (dirty) redrawSprites();
}
void AstronomicaEngine::stepPlace(int direction) {''')
# Only the real event loop, not script verification, advances animation implicitly.
s=s.replace('  runScripts();\n  _system->delayMillis', '  runScripts();\n  animateSpritesAt(scriptClock());\n  _system->delayMillis')
anchor='  // Full, unmodified P29 entry program:'
test='''  ConfMan.setBool("astronomica_animation", true);
  ConfMan.setBool("astronomica_sprite_input", true);
  bool animationOK = loadPlace(510) && _scene.sprites[1].selectedFrame == 0;
  clickAt(100,380); runScriptsAt(0); runScriptsAt(0);
  animationOK = _scene.sprites[1].visible && _runner.clicksBlocked() && animationOK;
  animateSpritesAt(399);
  animationOK = _scene.sprites[1].selectedFrame == 0 && animationOK;
  animateSpritesAt(400); runScriptsAt(400);
  animationOK = _scene.sprites[1].selectedFrame == 1 && !_runner.clicksBlocked() && animationOK;
  const uint32 animationFrameOneHash = screenRGBHash(_screen);
  animateSpritesAt(800);
  animationOK = _scene.sprites[1].selectedFrame == 0 && animationOK;
  const uint32 animationFrameZeroHash = screenRGBHash(_screen);
  animateSpritesAt(2400);
  animationOK = _scene.sprites[1].selectedFrame == 1 && animationOK;
  runScriptsAt(10399); animationOK = _scene.sprites[1].visible && animationOK;
  runScriptsAt(10400); animationOK = !_scene.sprites[1].visible && !_runner.pendingCount() && animationOK;
  animateSpritesAt(10400);
  animationOK = _scene.sprites[1].selectedFrame == 0 && animationOK;
  debug("Astronomica animation verification: %s (P510 original indicator click, hidden advancement, no catch-up; RGB %08x/%08x)", animationOK ? "PASS" : "FAIL", animationFrameZeroHash, animationFrameOneHash);
  scriptsOK = animationOK && scriptsOK;
  ConfMan.setBool("astronomica_animation", false);
  ConfMan.setBool("astronomica_sprite_input", false);
'''
s=s.replace(anchor,test+anchor);p.write_text(s)
for p in r.iterdir(): shutil.copy2(p,Path('work/fresh-20260913/scummvm/engines/astronomica')/p.name)
