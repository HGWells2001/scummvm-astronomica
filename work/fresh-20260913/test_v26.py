from pathlib import Path
import json,shutil
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp');s=p.read_text();rows=json.loads(Path('outputs/astronomica-cleanroom/evidence/staged/choices.json').read_text());anchor='  // Full, unmodified P29 entry program: repeated show/hide and self-call.'
block='''  bool stagedOK = loadPlace(508);
  const uint32 stagedRGB[] = {RGB};
  const uint32 staged565[] = {RGB565};
  _runner.seedRandom(1); uint32 seenChoices = 0;
  const Script stagedProgram = _scene.scripts[1];
  for (uint trial = 0; trial < 18; ++trial) {
   const uint32 before = screenRGBHash(_screen);
   stagedOK = _runner.enqueue(stagedProgram,0,true) && stagedOK;
   bool observedStaging = false;
   for (uint pass = 0; pass < 128 && _runner.pendingCount(); ++pass) {
    runScriptsAt(0);
    if (_pendingImage.w) { observedStaging = true; stagedOK = screenRGBHash(_screen) == before && stagedOK; }
   }
   int32 choice = 0; stagedOK = _runner.getValue(1,0,choice) && choice >= 1 && choice <= 18 && stagedOK;
   if (choice >= 1 && choice <= 18) {
    stagedOK = !(seenChoices & (1U << (choice-1))) &&
     screenRGBHash(_screen) == (rgb565 ? staged565[choice-1] : stagedRGB[choice-1]) && stagedOK;
    seenChoices |= 1U << (choice-1);
   }
   stagedOK = observedStaging && !_pendingImage.w && !_runner.pendingCount() && _place == 508 && stagedOK;
  }
  stagedOK = seenChoices == 0x3ffffU && stagedOK;
  // One staged image slot: a second load replaces the first without drawing.
  Script firstLoad, secondLoad, displayOnly;
  for (uint i = 0; i < stagedProgram.size(); ++i) {
   if (stagedProgram[i].opcode == 20) {
    if (firstLoad.empty()) firstLoad.push_back(stagedProgram[i]);
    else if (secondLoad.empty()) secondLoad.push_back(stagedProgram[i]);
   }
   if (stagedProgram[i].opcode == 49) displayOnly.push_back(stagedProgram[i]);
  }
  stagedOK = loadPlace(508) && stagedOK;
  const uint32 pristineImage = screenRGBHash(_screen);
  stagedOK = _runner.start(firstLoad,0,true) && stagedOK; applyScriptActions(0);
  stagedOK = _pendingImage.w && screenRGBHash(_screen) == pristineImage && stagedOK;
  stagedOK = _runner.start(secondLoad,0,true) && stagedOK; applyScriptActions(0);
  stagedOK = screenRGBHash(_screen) == pristineImage && _runner.start(displayOnly,0,true) && stagedOK; applyScriptActions(0);
  stagedOK = screenRGBHash(_screen) == (rgb565 ? staged565[1] : stagedRGB[1]) && !_pendingImage.w && stagedOK;
  stagedOK = _runner.start(firstLoad,0,true) && stagedOK; applyScriptActions(0);
  stagedOK = loadPlace(508) && !_pendingImage.w && _runner.start(displayOnly,0,true) && stagedOK; applyScriptActions(0);
  stagedOK = screenRGBHash(_screen) == pristineImage && stagedOK;
  debug("Astronomica staged image verification: %s (full original P508 script 1, all 18 variants, deferred display, slot replacement, reload cleanup)", stagedOK ? "PASS" : "FAIL");
  scriptsOK = stagedOK && scriptsOK;
'''.replace('RGB565',','.join('0x'+r['hashes']['565']+'U' for r in rows)).replace('RGB}',','.join('0x'+r['hashes']['888']+'U' for r in rows)+'}')
assert '={RGB' not in block
s=s.replace(anchor,block+anchor);p.write_text(s)
for f in p.parent.iterdir():
 if f.is_file(): shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
