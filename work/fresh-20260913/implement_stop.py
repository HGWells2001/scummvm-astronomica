from pathlib import Path
import shutil
r=Path('outputs/astronomica-cleanroom/engine/astronomica')
p=r/'script.cpp';s=p.read_text().replace('  case 9:', '  case 10:\n   if (c.args.size() != 1) return false;\n   break;\n  case 9:',1)
s=s.replace('if (c.opcode == 9 || c.opcode == 5', 'if (c.opcode == 10 || c.opcode == 9 || c.opcode == 5')
p.write_text(s)
p=r/'astronomica.cpp';s=p.read_text().replace(' while (_runner.popAction(action)) {', ' while (_runner.popAction(action)) {\n  if (action.opcode == 10) {\n   // _stop_sounds ignores its argument and calls sndPlaySound(NULL,1).\n   _mixer->stopHandle(_soundHandle);\n   continue;\n  }')
anchor='  // Full, unmodified P29 entry program:'
test='''  bool stopOK = loadPlace(501);
  Script originalStop;
  if (stopOK) for (uint i = 0; i < _scene.scripts[0].size(); ++i)
   if (_scene.scripts[0][i].opcode == 10) originalStop.push_back(_scene.scripts[0][i]);
  ConfMan.setBool("astronomica_audio", true);
  stopOK = loadPlace(510) && originalStop.size() == 1 && stopOK;
  stopOK = playSound(1) && _mixer->isSoundHandleActive(_soundHandle) && stopOK;
  stopOK = _runner.enqueue(originalStop,0,true) && stopOK;
  runScriptsAt(3499);
  stopOK = _mixer->isSoundHandleActive(_soundHandle) && _runner.pendingCount() == 1 && stopOK;
  runScriptsAt(3500);
  stopOK = !_mixer->isSoundHandleActive(_soundHandle) && !_runner.pendingCount() && stopOK;
  // Repeated stops are harmless. A following unknown opcode rejects the whole chain.
  stopOK = _runner.enqueue(originalStop,0,true) && stopOK;
  runScriptsAt(3500);
  stopOK = !_mixer->isSoundHandleActive(_soundHandle) && playSound(1) && stopOK;
  Script invalid = originalStop; Command unsupported; unsupported.opcode = 999; invalid.push_back(unsupported);
  stopOK = !_runner.start(invalid,0,true) && _mixer->isSoundHandleActive(_soundHandle) && stopOK;
  // Parameter is not used as a channel id in the original implementation.
  Script parameter = originalStop; parameter[0].args[0] = 123; parameter[0].delay = 0;
  stopOK = _runner.enqueue(parameter,0) && stopOK;
  runScriptsAt(0);
  stopOK = !_mixer->isSoundHandleActive(_soundHandle) && stopOK;
  ConfMan.setBool("astronomica_audio", false);
  debug("Astronomica stop verification: %s (original P501 command on P510 sound, 3499/3500 ms, repeated stop, atomic rejection)", stopOK ? "PASS" : "FAIL");
  scriptsOK = stopOK && scriptsOK;
'''
s=s.replace(anchor,test+anchor);p.write_text(s)
for p in r.iterdir(): shutil.copy2(p,Path('work/fresh-20260913/scummvm/engines/astronomica')/p.name)
