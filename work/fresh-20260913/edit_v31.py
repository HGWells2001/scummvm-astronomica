from pathlib import Path
import shutil
out=Path('outputs/astronomica-cleanroom');p=out/'engine/astronomica/astronomica.cpp';s=p.read_text()
marker='  ConfMan.setBool("astronomica_audio", false);\n  ConfMan.setBool("astronomica_sprite_input", false);\n  ConfMan.setBool("astronomica_animation", false);\n  // Full, unmodified P29'
assert marker in s
test='''  // P511: solve from the original initial conditions using only hit-tested clicks.
  bool controlsOK = true;
  for (uint route = 0; route < 3; ++route) {
   _runner.resetGlobals();
   controlsOK = loadPlace(511) && controlsOK;
   const uint completedBefore = _puzzlesCompleted;
   controlsOK = _runner.enqueueStartup(_scene.scripts,0,true) == 5 && controlsOK;
   uint32 now = 0;
   auto settle = [&]() {
    uint pass = 0;
    while (_runner.pendingCount() && pass++ < 1200) {
     runScriptsAt(now); animateSpritesAt(now); now += 50;
    }
    return !_runner.pendingCount() && !_runner.clicksBlocked();
   };
   auto valueIs = [&](int id, int expected) {
    int32 v = 0; return _runner.getValue(1,id,v) && v == expected;
   };
   auto press = [&](int sprite, int x, int y) {
    if (_place != 511 || _runner.clicksBlocked() || spriteAt(x,y) != sprite) return false;
    clickAtTime(x,y,now);
    if (!_runner.pendingCount()) return false;
    return settle();
   };
   controlsOK = settle() && valueIs(0,52) && valueIs(2,0) && valueIs(3,4) && valueIs(5,0) && controlsOK;
   if (route == 2) {
    controlsOK = press(1,35,430) && _place == 388 && controlsOK;
    int32 solved = -1;
    controlsOK = _runner.getValue(0,27,solved) && solved == 0 && _puzzlesCompleted == completedBefore && controlsOK;
    continue;
   }
   // Lower/upper clamp and reversible controls, before any solution.
   controlsOK = press(9,300,430) && valueIs(2,0) && controlsOK;
   controlsOK = press(17,534,443) && valueIs(0,52) && controlsOK;
   controlsOK = press(13,151,380) && valueIs(3,2) && controlsOK;
   controlsOK = press(14,179,380) && valueIs(3,3) && controlsOK;
   controlsOK = press(15,204,400) && valueIs(3,4) && controlsOK;
   auto setFirst = [&]() { return press(12,125,400) && valueIs(3,1); };
   auto setDial = [&]() {
    bool ok = true;
    for (int step = 1; step <= 15; ++step) ok = press(10,376,430) && valueIs(2,step) && ok;
    ok = press(10,376,430) && valueIs(2,15) && ok;
    ok = press(9,300,430) && valueIs(2,14) && ok;
    return press(10,376,430) && valueIs(2,15) && ok;
   };
   auto clearClouds = [&]() {
    bool ok = true;
    for (int step = 1; step <= 13; ++step) {
     ok = press(16,440,443) && ok;
     if (_place == 511) ok = valueIs(0,52-step*4) && ok;
    }
    return ok;
   };
   if (route == 0) {
    controlsOK = setFirst() && controlsOK;
    controlsOK = setDial() && controlsOK;
    controlsOK = clearClouds() && controlsOK;
   } else {
    controlsOK = clearClouds() && controlsOK;
    controlsOK = press(16,440,443) && valueIs(0,0) && controlsOK;
    controlsOK = press(17,534,443) && valueIs(0,4) && controlsOK;
    controlsOK = press(16,440,443) && valueIs(0,0) && controlsOK;
    controlsOK = setDial() && controlsOK;
    controlsOK = setFirst() && controlsOK;
   }
   int32 solved = 0;
   controlsOK = _place == 388 && _runner.getValue(0,27,solved) && solved == 1 &&
    _puzzlesCompleted == completedBefore+1 && controlsOK;
   debug("Astronomica P511 click route %u: %s (destination P%d, success=%d)",route,controlsOK ? "PASS" : "FAIL",_place,solved);
  }
  debug("Astronomica P511 interaction verification: %s (original initial state, hit-tested controls, bounds, reversal, two solution orders, unsolved exit)",controlsOK ? "PASS" : "FAIL");
  scriptsOK = controlsOK && scriptsOK;
'''
s=s.replace(marker,test+marker);p.write_text(s)
for f in (out/'engine/astronomica').iterdir():shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
