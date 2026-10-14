from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp')
s=p.read_text();anchor='  // Full, unmodified P29 entry program: repeated show/hide and self-call.'
assert anchor in s
s=s.replace(anchor,'''  ConfMan.setBool("astronomica_animation", true);
  bool rangeOK = loadPlace(511);
  Script originalRanges;
  if (rangeOK) for (uint i = 0; i < _scene.scripts[1].size(); ++i)
   if (_scene.scripts[1][i].opcode == 48) originalRanges.push_back(_scene.scripts[1][i]);
  rangeOK = originalRanges.size() == 4 && rangeOK;
  const uint32 rangeRGB[] = {0x413b4b5aU,0xc720b91eU,0xb9bea763U,0xb86c6b60U};
  const uint32 range565[] = {0x9b3c70e5U,0x606fe3c8U,0x4f281904U,0xffbd8bbbU};
  for (uint i = 0; i < originalRanges.size(); ++i) {
   Sprite &indicator = _scene.sprites[4];
   indicator.selectedFrame = 0; indicator.frameSince = 100;
   Script oneRange; oneRange.push_back(originalRanges[i]);
   rangeOK = _runner.enqueue(oneRange,100,true) && rangeOK; runScriptsAt(100);
   rangeOK = indicator.selectedFrame == 0 && indicator.frameSince == 100 &&
    indicator.frameFirst == originalRanges[i].args[1] && indicator.frameLast == originalRanges[i].args[2] && rangeOK;
   rangeOK = !advanceSpriteFrame(indicator,4,599) && rangeOK;
   // Only advance this indicator, keeping other scene sprites at their initial frames.
   for (uint tick = 1; tick <= 4; ++tick) {
    const int expected = i == 0 ? (tick % 2 ? 1 : 0) : i == 1 ? (tick % 2 ? 1 : 2) : (tick % 2 ? 3 : 2);
    rangeOK = advanceSpriteFrame(indicator,4,100 + tick * 500) && indicator.selectedFrame == expected && rangeOK;
    redrawSprites();
    rangeOK = screenRGBHash(_screen) == (rgb565 ? range565[expected] : rangeRGB[expected]) && rangeOK;
   }
  }
  if (!originalRanges.empty()) {
   Sprite &indicator = _scene.sprites[4];
   Script clamped; clamped.push_back(originalRanges[0]);
   clamped[0].args[1] = -50; clamped[0].args[2] = 99999;
   rangeOK = _runner.enqueue(clamped,0,true) && rangeOK; runScriptsAt(0);
   rangeOK = indicator.frameFirst == 0 && indicator.frameLast == 3 && rangeOK;
   const uint32 since = indicator.frameSince; const int frame = indicator.selectedFrame;
   Script badRange = clamped; badRange[0].args[1] = 3; badRange[0].args[2] = 1;
   rangeOK = !_runner.start(badRange,0,true) && rangeOK;
   Script atomicRange = clamped; Command unknownRange; unknownRange.opcode = 999; atomicRange.push_back(unknownRange);
   atomicRange[0].args[2] = 0;
   rangeOK = !_runner.start(atomicRange,0,true) && indicator.frameFirst == 0 && indicator.frameLast == 3 &&
    indicator.frameSince == since && indicator.selectedFrame == frame && rangeOK;
   badRange[0].args[0] = 9999;
   rangeOK = !_runner.start(badRange,0,true) && rangeOK;
  }
  debug("Astronomica range verification: %s (four original P511 commands, 500 ms, preserved frame/time, four independent RGB references, clamps, atomic rejection)", rangeOK ? "PASS" : "FAIL");
  scriptsOK = rangeOK && scriptsOK;
  ConfMan.setBool("astronomica_animation", false);
'''+anchor);p.write_text(s)
import shutil
for f in p.parent.iterdir():
 if f.is_file(): shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
