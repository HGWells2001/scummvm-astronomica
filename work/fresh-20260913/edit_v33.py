from pathlib import Path
import shutil
out=Path('outputs/astronomica-cleanroom');engine=out/'engine/astronomica'
p=engine/'script.cpp';s=p.read_text();old='if (opcode != 1 && opcode != 2 && opcode != 31 && opcode != 42 && opcode != 45) return false;'
new='''// State-only commands execute on the old scene before actions are applied.
   // Template calls merely enqueue work, which scene reload discards.
   // Visual/audio effects still need the original scene context and are rejected.
   if (opcode != 1 && opcode != 2 && opcode != 31 && opcode != 42 && opcode != 45 &&
       opcode != 32 && opcode != 33 && opcode != 39 && opcode != 40 && opcode != 46 && opcode != 41) return false;'''
assert old in s;s=s.replace(old,new);p.write_text(s)
p=engine/'astronomica.cpp';s=p.read_text().replace('if (!_runner.enqueue(r.click, now) && !r.click.empty())','if (!_runner.enqueue(r.click, now, ConfMan.hasKey("astronomica_sprite_input") && ConfMan.getBool("astronomica_sprite_input")) && !r.click.empty())')
marker='  // P511: solve from the original initial conditions using only hit-tested clicks.'
test='''  bool skyOK = true;
  for (uint route = 0; route < 2; ++route) {
   _runner.resetGlobals();
   skyOK = loadPlace(509) && skyOK;
   const uint completedBefore = _puzzlesCompleted;
   const uint skyEntries = _runner.enqueueStartup(_scene.scripts,0,true);
   skyOK = skyEntries == 6 && skyOK;
   debug("Astronomica P509 test startup: %u/6",skyEntries);
   uint32 now = 0;
   auto advance = [&](uint32 duration) {
    const uint32 end = now + duration;
    while (now < end && _place == 509) { runScriptsAt(now); animateSpritesAt(now); now += 50; }
   };
   auto valueIs = [&](int id, int expected) { int32 v = -1; return _runner.getValue(1,id,v) && v == expected; };
   auto choose = [&](int option) {
    const int xs[] = {83,166,257,338,408,490};
    if (_place != 509 || _runner.clicksBlocked() || spriteAt(xs[option-1],365) != option+3) return false;
    clickAtTime(xs[option-1],365,now); advance(1000);
    return !_runner.clicksBlocked() && valueIs(7,option);
   };
   auto target = [&](int rect) {
    if (_place != 509 || _runner.clicksBlocked()) return false;
    const MouseRect &r = _scene.mouseRects[rect];
    const int x = (r.rect[0]+r.rect[2])/2, y = (r.rect[1]+r.rect[3])/2;
    if (spriteAt(x,y) != -1) return false;
    clickAtTime(x,y,now); advance(2000);
    return _place != 509 || !_runner.clicksBlocked();
   };
   advance(4000);
   skyOK = valueIs(15,1) && valueIs(16,2) && !_runner.clicksBlocked() && skyOK;
   if (route == 0) {
    // Remove all six sources, then the remaining sources in the second sky.
    const int order[] = {0,1,2,4,3,5}, options[] = {2,1,1,2,1,3};
    for (uint i = 0; i < 6; ++i) {
     const bool selected = choose(options[i]), clicked = target(order[i]);
     skyOK = selected && clicked && skyOK;
     debug("Astronomica P509 target %d: selected=%d clicked=%d",order[i],selected,clicked);
    }
    skyOK = valueIs(16,1) && skyOK;
    skyOK = choose(1) && target(3) && skyOK;
    skyOK = choose(3) && target(5) && skyOK;
    advance(30000);
   } else {
    // Three wrong classifications must take the original failure route.
    skyOK = choose(3) && skyOK;
    for (int i = 0; i < 3; ++i) skyOK = target(0) && skyOK;
    advance(20000);
   }
   int32 solved = -1;
   skyOK = _place == 304 && _runner.getValue(0,25,solved) && solved == (route ? 0 : 1) &&
    _puzzlesCompleted == completedBefore+(route ? 0 : 1) && skyOK;
   debug("Astronomica P509 route %u: %s (destination P%d, success=%d)",route,skyOK ? "PASS" : "FAIL",_place,solved);
  }
  debug("Astronomica P509 interaction verification: %s (original startup, timed image hotspots, two skies, three-error route)",skyOK ? "PASS" : "FAIL");
  scriptsOK = skyOK && scriptsOK;
'''
assert marker in s;s=s.replace(marker,test+marker);p.write_text(s)
for f in engine.iterdir():shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
