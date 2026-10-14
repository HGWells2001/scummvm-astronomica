from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp');s=p.read_text();anchor='  // Full, unmodified P29 entry program: repeated show/hide and self-call.'
s=s.replace(anchor,'''  // Isolated original loop controls; no assumption that the full puzzle runs.
  bool loopOK = loadPlace(509);
  Script disableLoop, enableLoop, chooseLoop;
  if (loopOK) {
   for (uint i = 0; i < _scene.scripts[2].size(); ++i)
    if (_scene.scripts[2][i].opcode == 25 && disableLoop.empty()) disableLoop.push_back(_scene.scripts[2][i]);
   for (uint i = 0; i < _scene.scripts[4].size(); ++i)
    if (_scene.scripts[4][i].opcode == 26) enableLoop.push_back(_scene.scripts[4][i]);
  }
  loopOK = loadPlace(511) && loopOK;
  if (loopOK) for (uint i = 0; i < _scene.scripts[0].size(); ++i)
   if (_scene.scripts[0][i].opcode == 27) chooseLoop.push_back(_scene.scripts[0][i]);
  loopOK = chooseLoop.size() == 1 && disableLoop.size() == 1 && enableLoop.size() == 1 && loopOK;
  Audio::SeekableAudioStream *loopSource = openSound(12);
  loopOK = loopSource && loopOK;
  if (loopSource) {
   Audio::AudioStream *repeating = Audio::makeLoopingAudioStream(loopSource,0);
   int16 repeated[3705];
   loopOK = repeating->readBuffer(repeated,3705) == 3705 && !repeating->endOfData() && loopOK;
   uint32 pcmHash = 2166136261U;
   for (uint i = 0; i < 1834; ++i) {
    pcmHash = (pcmHash ^ (uint16(repeated[i]) & 255)) * 16777619U;
    pcmHash = (pcmHash ^ (uint16(repeated[i]) >> 8)) * 16777619U;
    loopOK = repeated[i] == repeated[i+1834] && loopOK;
   }
   for (uint i = 0; i < 37; ++i) loopOK = repeated[i] == repeated[i+3668] && loopOK;
   loopOK = pcmHash == 0xad03e6daU && loopOK;
   delete repeating;
  }
  loopOK = _runner.enqueue(chooseLoop,0,true) && loopOK; runScriptsAt(0);
  const uint beforeLoop = _soundsStarted;
  resumeLoopAt(5000);
  loopOK = _soundsStarted == beforeLoop && !_mixer->isSoundHandleActive(_soundHandle) && loopOK;
  resumeLoopAt(5001);
  loopOK = _soundsStarted == beforeLoop+1 && _lastSound == 12 && _mixer->isSoundHandleActive(_soundHandle) && loopOK;
  resumeLoopAt(9000);
  loopOK = _soundsStarted == beforeLoop+1 && loopOK;
  Script foreground; Command fg; fg.opcode = 9; fg.args.push_back(2); foreground.push_back(fg);
  loopOK = _runner.enqueue(foreground,6000) && loopOK; runScriptsAt(6000);
  resumeLoopAt(11001); // Long foreground sound is still active despite elapsed logical time.
  loopOK = _lastSound == 2 && _soundsStarted == beforeLoop+2 && _lastSoundAt == 6000 && loopOK;
  _mixer->stopHandle(_soundHandle); // Simulate foreground completion without a wall-clock wait.
  resumeLoopAt(11000);
  loopOK = _soundsStarted == beforeLoop+2 && loopOK;
  resumeLoopAt(11001);
  loopOK = _soundsStarted == beforeLoop+3 && _lastSound == 12 && loopOK;
  loopOK = _runner.enqueue(disableLoop,12000,true) && loopOK; runScriptsAt(12000); resumeLoopAt(20000);
  loopOK = !_loopEnabled && !_mixer->isSoundHandleActive(_soundHandle) && _soundsStarted == beforeLoop+3 && loopOK;
  loopOK = _runner.enqueue(enableLoop,20000,true) && loopOK; runScriptsAt(20000); resumeLoopAt(20000);
  loopOK = _loopEnabled && _soundsStarted == beforeLoop+4 && _mixer->isSoundHandleActive(_soundHandle) && loopOK;
  Script badLoop = chooseLoop; badLoop[0].args[0] = 899;
  loopOK = !_runner.enqueue(badLoop,0,true) && _loopSound == 12 && _mixer->isSoundHandleActive(_soundHandle) && loopOK;
  loopOK = loadPlace(103) && loopOK; resumeLoopAt(30000);
  loopOK = _loopSound == -1 && !_mixer->isSoundHandleActive(_soundHandle) && loopOK;
  debug("Astronomica loop verification: %s (original P511/P509 controls, S12 PCM wrap, 5000/5001 ms, foreground priority, disable/enable, scene cleanup)", loopOK ? "PASS" : "FAIL");
  scriptsOK = loopOK && scriptsOK;
'''+anchor);p.write_text(s)
import shutil
for f in p.parent.iterdir():
 if f.is_file(): shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
