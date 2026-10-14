from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.h');s=p.read_text().replace(' uint32 _puzzlesCompleted = 0;',' uint32 _puzzlesCompleted = 0, _lastSuccessEnd = 0;');p.write_text(s)
p=p.with_name('astronomica.cpp');s=p.read_text().replace(' return now + uint32(_system->getMillis() - started);',' _lastSuccessEnd = now + uint32(_system->getMillis() - started);\n return _lastSuccessEnd;');anchor='  // Full, unmodified P29 entry program: repeated show/hide and self-call.'
s=s.replace(anchor,'''  ConfMan.setBool("astronomica_audio", true);
  bool successOK = loadPlace(511);
  Script originalSuccess;
  if (successOK) for (uint i = 0; i < _scene.scripts[0].size(); ++i)
   if (_scene.scripts[0][i].opcode == 23) originalSuccess.push_back(_scene.scripts[0][i]);
  successOK = originalSuccess.size() == 1 && successOK;
  _runner.defineValue(0,27,0);
  const uint32 initialCompleted = _puzzlesCompleted;
  const uint successSounds = _soundsStarted;
  Script invalidSuccess = originalSuccess; Command unrecognizedSuccess; unrecognizedSuccess.opcode = 999;
  invalidSuccess.push_back(unrecognizedSuccess);
  successOK = !_runner.start(invalidSuccess,0,true) && _puzzlesCompleted == initialCompleted && successOK;
  successOK = _runner.start(originalSuccess,100,true) && successOK;
  int32 completionFlag = 0;
  successOK = _runner.getValue(0,27,completionFlag) && completionFlag == 1 && _puzzlesCompleted == initialCompleted+1 &&
   _soundsStarted == successSounds+1 && _lastSound == 912 && !_mixer->isSoundHandleActive(_soundHandle) && _lastSuccessEnd > 100 && successOK;
  successOK = _runner.start(originalSuccess,200,true) && _puzzlesCompleted == initialCompleted+1 && _soundsStarted == successSounds+1 && successOK;
  _runner.defineValue(0,27,-2);
  successOK = _runner.start(originalSuccess,300,true) && _runner.getValue(0,27,completionFlag) && completionFlag == 1 &&
   _puzzlesCompleted == initialCompleted+1 && _soundsStarted == successSounds+1 && successOK;
  // A queued continuation is timed from the end of synchronous playback.
  _runner.defineValue(0,27,0); _runner.defineValue(1,4,1);
  Script afterSuccess = originalSuccess; Command continuation;
  continuation.opcode = 32; continuation.delay = 1000;
  continuation.args.push_back(1); continuation.args.push_back(4); continuation.args.push_back(99); afterSuccess.push_back(continuation);
  successOK = _runner.start(afterSuccess,400,true) && successOK;
  runScriptsAt(_lastSuccessEnd+999);
  successOK = _runner.getValue(1,4,completionFlag) && completionFlag == 1 && successOK;
  runScriptsAt(_lastSuccessEnd+1000);
  successOK = _runner.getValue(1,4,completionFlag) && completionFlag == 99 && _puzzlesCompleted == initialCompleted+2 && successOK;
  successOK = loadPlace(103) && _runner.getValue(0,27,completionFlag) && completionFlag == 1 &&
   !_runner.canRun(originalSuccess,true) && successOK;
  successOK = loadPlace(1) && _runner.getValue(0,27,completionFlag) && completionFlag == 0 && successOK;
  ConfMan.setBool("astronomica_audio", false);
  successOK = loadPlace(511) && !_runner.canRun(originalSuccess,true) && successOK;
  debug("Astronomica success verification: %s (original P511 custom 25, global 27, synchronous S12, duplicate suppression, continuation timing, scene persistence, P1 reset)", successOK ? "PASS" : "FAIL");
  scriptsOK = successOK && scriptsOK;
'''+anchor);p.write_text(s)
import shutil
for f in p.parent.iterdir():
 if f.is_file(): shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
