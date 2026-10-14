from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica/script.cpp');s=p.read_text();old='''   // A queued successor is discarded by the original scene-load cleanup.
   // Immediate successors can still act on the old scene after requesting a
   // transition; leave those chains unsupported until that ordering is covered.
   if (i + 1 < script.size() && script[i + 1].delay == -1) return false;''';new='''   // The original sets a scene-change request, then completes immediate
   // branch control before _do_place reloads. Admit control-only immediate
   // tails; effects on the old scene still need deferred transition handling.
   // Check the whole suffix because conditional links can jump past a delay.
   for (uint tail = i + 1; tail < script.size(); ++tail) {
    const Command &next = script[tail];
    if (next.delay == -1 && next.opcode != 1 && next.opcode != 2 &&
        next.opcode != 31 && next.opcode != 42 && next.opcode != 45) return false;
   }''';assert old in s;s=s.replace(old,new);p.write_text(s)
p=p.with_name('astronomica.cpp');s=p.read_text();anchor='  // Full, unmodified P29 entry program: repeated show/hide and self-call.';s=s.replace(anchor,'''  ConfMan.setBool("astronomica_audio", true);
  ConfMan.setBool("astronomica_animation", true);
  bool endingOK = loadPlace(511);
  // Set the solved input state, then run the ENTIRE original ending script.
  // This exercises the ending sequence, not the player solving the puzzle.
  _runner.defineValue(1,5,7); _runner.defineValue(0,27,0);
  const uint32 completedBeforeEnding = _puzzlesCompleted;
  Script fullEnding = _scene.scripts[0];
  endingOK = _runner.canRun(fullEnding,true) && _runner.enqueue(fullEnding,0,true) && endingOK;
  for (uint i = 0; i < 6; ++i) runScriptsAt(0);
  endingOK = _place == 511 && _scene.sprites[19].x == 190 && _scene.sprites[19].y == 220 && _runner.clicksBlocked() && endingOK;
  const int routeX[] = {220,250,280,310,340,370,400};
  const int routeY[] = {215,210,205,205,210,210,215};
  for (uint i = 0; i < 7; ++i) {
   runScriptsAt((i+1)*300-1);
   endingOK = _scene.sprites[19].x == (i ? routeX[i-1] : 190) && endingOK;
   runScriptsAt((i+1)*300);
   endingOK = _place == 511 && _scene.sprites[19].x == routeX[i] && _scene.sprites[19].y == routeY[i] && endingOK;
  }
  runScriptsAt(7099);
  endingOK = _puzzlesCompleted == completedBeforeEnding && _place == 511 && endingOK;
  runScriptsAt(7100);
  endingOK = _puzzlesCompleted == completedBeforeEnding+1 && _runner.getValue(0,27,completionFlag) && completionFlag == 1 && endingOK;
  runScriptsAt(_lastSuccessEnd+999);
  endingOK = _place == 511 && endingOK;
  runScriptsAt(_lastSuccessEnd+1000);
  endingOK = _place == 388 && !_runner.pendingCount() && !_runner.clicksBlocked() &&
   _runner.getValue(0,27,completionFlag) && completionFlag == 1 && endingOK;
  // The same full program takes the other branch when not solved.
  endingOK = loadPlace(511) && endingOK;
  _runner.defineValue(1,5,0);
  Script lockInput; Command lock; lock.opcode = 28; lock.args.push_back(-1); lockInput.push_back(lock);
  endingOK = _runner.start(lockInput,0) && _runner.enqueue(_scene.scripts[0],0,true) && endingOK;
  runScriptsAt(0); runScriptsAt(0); runScriptsAt(74);
  endingOK = _runner.clicksBlocked() && _place == 511 && endingOK;
  runScriptsAt(75);
  endingOK = !_runner.clicksBlocked() && _place == 511 && _puzzlesCompleted == completedBeforeEnding+1 && endingOK;
  // Keep an immediate scene effect unsupported even after a control command.
  Script unsafeEnding = fullEnding;
  for (uint i = 0; i < unsafeEnding.size(); ++i) if (unsafeEnding[i].opcode == 45) {
   Command effect; effect.opcode = 17; effect.delay = -1; effect.args.push_back(5);
   unsafeEnding.insert_at(i+1,effect); break;
  }
  endingOK = !_runner.canRun(unsafeEnding,true) && endingOK;
  debug("Astronomica ending verification: %s (complete original P511 script 0, eight positions, success sound, P388 transition, unsolved branch, unsafe tail rejection)", endingOK ? "PASS" : "FAIL");
  scriptsOK = endingOK && scriptsOK;
  ConfMan.setBool("astronomica_animation", false);
  ConfMan.setBool("astronomica_audio", false);
'''+anchor);p.write_text(s)
import shutil
for f in p.parent.iterdir():
 if f.is_file(): shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
