from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica')
f=p/'script.cpp';s=f.read_text().replace('if (c.opcode == 9 &&','if ((c.opcode == 9 || c.opcode == 27) &&');s=s.replace('case 10:\n', 'case 25: case 26:\n   if (!c.args.empty()) return false;\n   break;\n  case 10:\n');s=s.replace('case 9:\n','case 9: case 27:\n');s=s.replace('if (c.opcode == 10 || c.opcode == 9 ||', 'if (c.opcode == 25 || c.opcode == 26 || c.opcode == 27 || c.opcode == 10 || c.opcode == 9 ||');s=s.replace('Action action = { c.opcode, c.opcode == 9 ||', 'Action action = { c.opcode, c.opcode == 27 || c.opcode == 9 ||');f.write_text(s)
f=p/'astronomica.h';s=f.read_text().replace('bool playSound(int id);', 'bool playSound(int id, uint32 now = 0, bool looping = false);\n void resumeLoopAt(uint32 now);\n int _loopSound = -1;\n bool _loopEnabled = true;\n uint32 _lastSoundAt = 0;');s=s.replace('void applyScriptActions();','void applyScriptActions(uint32 now);');f.write_text(s)
f=p/'astronomica.cpp';s=f.read_text().replace('_scene = parsed;', '_loopSound = -1; _loopEnabled = true; _lastSoundAt = 0;\n _scene = parsed;');s=s.replace('bool AstronomicaEngine::playSound(int id) {','bool AstronomicaEngine::playSound(int id, uint32 now, bool looping) {');s=s.replace('_mixer->playStream(Audio::Mixer::kSFXSoundType, &_soundHandle, stream);','_mixer->playStream(Audio::Mixer::kSFXSoundType, &_soundHandle, looping ? Audio::makeLoopingAudioStream(stream, 0) : stream);\n if (!looping) _lastSoundAt = now;');s=s.replace('bool AstronomicaEngine::verifyAudio() {','''void AstronomicaEngine::resumeLoopAt(uint32 now) {
 // _playLoop 9:3c29 probes with SND_NOSTOP. A playing foreground sound
 // must finish before the loop can resume. Puzzle scenes also wait >5 s.
 if (_loopSound < 0 || !_loopEnabled || _mixer->isSoundHandleActive(_soundHandle)) return;
 if (_place >= 500 && _place <= 550 && uint32(now - _lastSoundAt) <= 5000) return;
 if (!playSound(_loopSound, now, true)) _loopSound = -1;
}
bool AstronomicaEngine::verifyAudio() {''');s=s.replace('applyScriptActions();','applyScriptActions(scriptClock());');s=s.replace('_runner.tick(now);\n applyScriptActions(scriptClock());','_runner.tick(now);\n applyScriptActions(now);');s=s.replace('void AstronomicaEngine::applyScriptActions() {','void AstronomicaEngine::applyScriptActions(uint32 now) {');s=s.replace('  if (action.opcode == 10) {','''  if (action.opcode == 25) {
   _loopEnabled = false; _mixer->stopHandle(_soundHandle); continue;
  }
  if (action.opcode == 26) { _loopEnabled = true; continue; }
  if (action.opcode == 27) {
   _mixer->stopHandle(_soundHandle); _loopSound = action.value; _lastSoundAt = 0;
   continue;
  }
  if (action.opcode == 10) {''');s=s.replace('if (!playSound(action.value))','if (!playSound(action.value, now))');s=s.replace('animateSpritesAt(scriptClock());','animateSpritesAt(scriptClock());\n  resumeLoopAt(scriptClock());');f.write_text(s)
