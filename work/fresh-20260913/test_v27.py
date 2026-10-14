from pathlib import Path
import shutil
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.h');s=p.read_text().replace(' void clickAt(int x, int y);', ' void clickAt(int x, int y);\n void clickAtTime(int x, int y, uint32 now);');p.write_text(s)
p=p.with_name('astronomica.cpp');s=p.read_text();a=s.index('void AstronomicaEngine::clickAt(int x, int y) {');b=s.index('uint32 AstronomicaEngine::scriptClock()',a);part=s[a:b].replace('void AstronomicaEngine::clickAt(int x, int y) {','void AstronomicaEngine::clickAt(int x, int y) { clickAtTime(x,y,scriptClock()); }\nvoid AstronomicaEngine::clickAtTime(int x, int y, uint32 now) {').replace('scriptClock()', 'now');part=part.replace('clickAtTime(x,y,now);','clickAtTime(x,y,scriptClock());',1);s=s[:a]+part+s[b:];anchor='  // Full, unmodified P29 entry program: repeated show/hide and self-call.'
s=s.replace(anchor,'''  ConfMan.setBool("astronomica_audio", true);
  ConfMan.setBool("astronomica_sprite_input", true);
  ConfMan.setBool("astronomica_animation", true);
  bool answersOK = true;
  for (uint wrong = 0; wrong < 2; ++wrong) {
   _runner.resetGlobals(); _runner.seedRandom(1);
   answersOK = loadPlace(508) && answersOK;
   const uint32 completedBefore = _puzzlesCompleted;
   answersOK = _runner.enqueueStartup(_scene.scripts,0,true) == 3 && answersOK;
   uint32 answerTime = 0;
   for (uint pass = 0; pass < 128 && _runner.pendingCount(); ++pass) { runScriptsAt(answerTime); answerTime += 50; }
   answersOK = !_runner.pendingCount() && !_runner.clicksBlocked() && answersOK;
   const uint count = wrong ? 3 : 8;
   for (uint answer = 0; answer < count && _place == 508; ++answer) {
    int32 choice = 0; answersOK = _runner.getValue(1,0,choice) && choice >= 1 && choice <= 18 && answersOK;
    const bool upper = (choice > 12) != bool(wrong);
    const int x = upper ? 223 : 222, y = upper ? 188 : 253;
    answersOK = spriteAt(x,y) == (upper ? 4 : 6) && answersOK;
    clickAtTime(x,y,answerTime);
    answersOK = _runner.pendingCount() > 0 && answersOK;
    // Drive the same input/scheduler paths as the interactive loop.
    for (uint pass = 0; pass < 1200 && _place == 508 && _runner.pendingCount(); ++pass) {
     runScriptsAt(answerTime); animateSpritesAt(answerTime); answerTime += 50;
    }
    if (answer+1 < count) {
     int32 score = 0;
     answersOK = _place == 508 && !_runner.clicksBlocked() && !_runner.pendingCount() &&
      _runner.getValue(1,wrong ? 3 : 4,score) && score == int32(answer+1) && answersOK;
    }
   }
   int32 solved = 0;
   answersOK = _place == 388 && !_runner.pendingCount() && _runner.getValue(0,24,solved) &&
    solved == (wrong ? 0 : 1) && _puzzlesCompleted == completedBefore+(wrong ? 0 : 1) && answersOK;
   debug("Astronomica P508 %s route: %s (destination P%d, success=%d)",wrong ? "three-error" : "eight-answer",answersOK ? "PASS" : "FAIL",_place,solved);
  }
  debug("Astronomica P508 interaction verification: %s (original startup and click programs, eight correct answers and three-error exit)",answersOK ? "PASS" : "FAIL");
  scriptsOK = answersOK && scriptsOK;
  ConfMan.setBool("astronomica_audio", false);
  ConfMan.setBool("astronomica_sprite_input", false);
  ConfMan.setBool("astronomica_animation", false);
'''+anchor);p.write_text(s)
for f in p.parent.iterdir():
 if f.is_file(): shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
