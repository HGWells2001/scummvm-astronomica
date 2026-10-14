from pathlib import Path
import shutil
out=Path('outputs/astronomica-cleanroom'); engine=out/'engine/astronomica'
p=engine/'resource.h';s=p.read_text().replace('int32 mode = 0, nav[3] = {}, layers = 0;', 'int32 mode = 0, nav[3] = {}, layers = 0;\n bool introSound = false;\n int32 introSoundId = -1;');p.write_text(s)
p=engine/'resource.cpp';s=p.read_text().replace('if (flag()) number();\n scene.layers', 'scene.introSound = flag();\n if (scene.introSound) scene.introSoundId = number();\n scene.layers');p.write_text(s)
p=engine/'astronomica.cpp';s=p.read_text();old=' if (ConfMan.hasKey("astronomica_entry_scripts") && ConfMan.getBool("astronomica_entry_scripts")) queueEntryScripts();'
new=''' if (ConfMan.hasKey("astronomica_entry_scripts") && ConfMan.getBool("astronomica_entry_scripts")) {
  // Reconstructed mode-0 audio lifecycle (_load_place 9:156b, 1c45,
  // 2f22). Other scene modes have separate global ambience rules.
  if (_scene.mode == 0 && ConfMan.hasKey("astronomica_audio") && ConfMan.getBool("astronomica_audio")) {
   Audio::SeekableAudioStream *music = openSound(0);
   if (music) { _loopSound = 0; delete music; }
   // Intro IDs are direct file IDs, not serialized command operands.
   // The original skips the intro on return from P408 (help).
   if (_scene.introSound && _scene.movies.empty() && _previousPlace != 408 && playSound(_scene.introSoundId, scriptClock())) {
    debug("Astronomica P%d introduction: S%d.WAV", _place, _scene.introSoundId);
    while (_mixer->isSoundHandleActive(_soundHandle) && !shouldQuit()) {
     Common::Event event;
     while (_system->getEventManager()->pollEvent(event))
      if (event.type == Common::EVENT_QUIT) quitGame();
     _system->updateScreen();
     _system->delayMillis(5);
    }
   }
   _lastSoundAt = 0; // Original resets this after scene loading.
  }
  if (!shouldQuit()) queueEntryScripts();
 }'''
assert old in s;s=s.replace(old,new)
s=s.replace(' if (!playSound(_loopSound, now, true)) _loopSound = -1;', ' if (!playSound(_loopSound, now, true)) _loopSound = -1;\n else debug("Astronomica P%d loop: S%d.WAV", _place, _loopSound);')
marker='  bool answersOK = true;'
test='''  // Exercise the actual scene-entry path, including complete intro playback.
  ConfMan.setBool("astronomica_entry_scripts", true);
  const uint beforeIntro = _soundsStarted;
  bool entryAudioOK = loadPlace(508) && _scene.introSound && _scene.introSoundId == 302 &&
   _lastSound == 302 && _soundsStarted == beforeIntro+1 && !_mixer->isSoundHandleActive(_soundHandle) &&
   _loopSound == 0 && _runner.pendingCount() == 3;
  resumeLoopAt(5000);
  entryAudioOK = _soundsStarted == beforeIntro+1 && entryAudioOK;
  resumeLoopAt(5001);
  entryAudioOK = _lastSound == 0 && _soundsStarted == beforeIntro+2 && _mixer->isSoundHandleActive(_soundHandle) && entryAudioOK;
  playSound(8,6000);
  resumeLoopAt(12000);
  entryAudioOK = _lastSound == 8 && entryAudioOK;
  _mixer->stopHandle(_soundHandle); resumeLoopAt(12000);
  entryAudioOK = _lastSound == 0 && entryAudioOK;
  ConfMan.setBool("astronomica_entry_scripts", false);
  entryAudioOK = loadPlace(103) && _loopSound == -1 && !_mixer->isSoundHandleActive(_soundHandle) && entryAudioOK;
  ConfMan.setBool("astronomica_audio", false);
  ConfMan.setBool("astronomica_entry_scripts", true);
  const uint beforeSilentEntry = _soundsStarted;
  entryAudioOK = loadPlace(508) && _soundsStarted == beforeSilentEntry && _loopSound == -1 && entryAudioOK;
  ConfMan.setBool("astronomica_entry_scripts", false);
  ConfMan.setBool("astronomica_audio", true);
  debug("Astronomica entry audio verification: %s (P508 S302 intro completes before scripts, default S0 loop, foreground priority, reload cleanup, audio disabled)", entryAudioOK ? "PASS" : "FAIL");
  scriptsOK = entryAudioOK && scriptsOK;
'''
assert marker in s;s=s.replace(marker,test+marker);p.write_text(s)
for f in engine.iterdir():shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
