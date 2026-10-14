from pathlib import Path
import shutil
r=Path('outputs/astronomica-cleanroom/engine/astronomica')
p=r/'script.h';s=p.read_text().replace(' void setSpriteTargets', ' void setSoundTargets(const Common::Array<bool> &targets) { _soundTargets = targets; }\n void setSpriteTargets').replace(' Common::Array<uint> _spriteTargets;', ' Common::Array<uint> _spriteTargets;\n Common::Array<bool> _soundTargets;');p.write_text(s)
p=r/'script.cpp';s=p.read_text().replace(' _spriteTargets.clear();',' _spriteTargets.clear();\n _soundTargets.clear();')
s=s.replace('  if (c.opcode == 41) {','  if (c.opcode == 9 && (uint(c.args[0]) >= _soundTargets.size() || !_soundTargets[c.args[0]])) return false;\n  if (c.opcode == 41) {',1)
s=s.replace('  case 28: case 29:', '  case 9:\n   if (c.args.size() != 1 || c.args[0] < 0 || c.args[0] >= 900) return false;\n   break;\n  case 28: case 29:',1)
s=s.replace('if (c.opcode == 5 || c.opcode == 6', 'if (c.opcode == 9 || c.opcode == 5 || c.opcode == 6')
s=s.replace('c.opcode == 5 || c.opcode == 7 ||', 'c.opcode == 9 || c.opcode == 5 || c.opcode == 7 ||')
p.write_text(s)
p=r/'astronomica.h';s=p.read_text().replace('#include "engines/engine.h"', '#include "engines/engine.h"\n#include "audio/mixer.h"\nnamespace Audio { class SeekableAudioStream; }')
s=s.replace(' Common::Error run() override;', ' ~AstronomicaEngine() override { _mixer->stopHandle(_soundHandle); }\n Common::Error run() override;')
s=s.replace(' ScriptRunner _runner;', ' ScriptRunner _runner;\n Audio::SoundHandle _soundHandle;\n uint _soundsStarted = 0;\n int _lastSound = -1;\n Audio::SeekableAudioStream *openSound(int id);\n void configureSounds();\n bool playSound(int id);\n bool verifyAudio();');p.write_text(s)
p=r/'astronomica.cpp';s=p.read_text().replace('#include "astronomica/sprites.h"','#include "astronomica/sprites.h"\n#include "audio/decoders/wave.h"\n#include "audio/audiostream.h"')
s=s.replace(' _scene = parsed;', ' _mixer->stopHandle(_soundHandle);\n _scene = parsed;')
s=s.replace(' _place = place;', ' _place = place;\n configureSounds();')
anchor='void AstronomicaEngine::presentScene() {'
code='''Audio::SeekableAudioStream *AstronomicaEngine::openSound(int id) {
 if (id < 0 || id >= 900) return nullptr;
 Common::File *file = new Common::File();
 const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d/S%d.WAV", _place, id)));
 if (!file->open(Common::FSNode(path))) { delete file; return nullptr; }
 return Audio::makeWAVStream(file, DisposeAfterUse::YES);
}
void AstronomicaEngine::configureSounds() {
 Common::Array<bool> targets; targets.resize(900);
 for (uint i = 0; i < targets.size(); ++i) targets[i] = false;
 if (ConfMan.hasKey("astronomica_audio") && ConfMan.getBool("astronomica_audio")) {
  Common::FSList files;
  const Common::Path folder = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d", _place)));
  Common::FSNode(folder).getChildren(files, Common::FSNode::kListFilesOnly);
  for (uint i = 0; i < files.size(); ++i) {
   Common::String name = files[i].getName(); name.toUppercase();
   if (!name.hasPrefix("S") || !name.hasSuffix(".WAV")) continue;
   const int id = atoi(name.c_str() + 1);
   if (id < 0 || id >= 900 || name != Common::String::format("S%d.WAV", id)) continue;
   // Original exceptions play synchronously; don't silently make them async.
   if ((_place == 505 && id >= 2 && id <= 10) || (_place == 512 && id == 14)) continue;
   Common::File file;
   if (!file.open(files[i])) continue;
   int size, rate; byte flags; uint16 type;
   if (Audio::loadWAVFromStream(file, size, rate, flags, &type) && type == 1)
    targets[id] = true;
  }
 }
 _runner.setSoundTargets(targets);
}
bool AstronomicaEngine::playSound(int id) {
 Audio::SeekableAudioStream *stream = openSound(id);
 if (!stream) return false;
 // sndPlaySound is a single channel; a new sound replaces the old one.
 _mixer->stopHandle(_soundHandle);
 _mixer->playStream(Audio::Mixer::kSFXSoundType, &_soundHandle, stream);
 _lastSound = id; ++_soundsStarted;
 return true;
}
bool AstronomicaEngine::verifyAudio() {
 struct Reference { int id; uint samples; uint32 hash; };
 const Reference refs[] = { {2,3627,0}, {3,4272,0}, {6,23808,0} };
 bool ok = true;
 for (uint i = 0; i < ARRAYSIZE(refs); ++i) {
  Audio::SeekableAudioStream *stream = openSound(refs[i].id);
  if (!stream) return false;
  ok = stream->getRate() == 11025 && !stream->isStereo() && ok;
  int16 samples[1024]; uint count = 0; uint32 hash = 2166136261U;
  for (;;) {
   const int n = stream->readBuffer(samples, ARRAYSIZE(samples));
   if (n <= 0) break;
   count += n;
   for (int j = 0; j < n; ++j) {
    const uint16 v = uint16(samples[j]);
    hash = (hash ^ (v & 255)) * 16777619U;
    hash = (hash ^ (v >> 8)) * 16777619U;
   }
  }
  delete stream;
  debug("Astronomica audio samples: P510/S%d.WAV %u %08x", refs[i].id, count, hash);
  ok = count == refs[i].samples && (refs[i].hash == 0 || hash == refs[i].hash) && ok;
 }
 return ok;
}
'''
s=s.replace(anchor,code+anchor)
s=s.replace(' while (_runner.popAction(action)) {',' while (_runner.popAction(action)) {\n  if (action.opcode == 9) {\n   if (!playSound(action.value)) warning("Astronomica: cannot play sound %d in P%d", action.value, _place);\n   continue;\n  }')
anchor='  // Full, unmodified P29 entry program:'
test='''  ConfMan.setBool("astronomica_audio", true);
  ConfMan.setBool("astronomica_sprite_input", true);
  bool audioOK = loadPlace(510) && verifyAudio();
  const uint soundCountBefore = _soundsStarted;
  clickAt(30,375); // Original type-2 button: pulse, sound S3, unlock.
  audioOK = _soundsStarted == soundCountBefore && audioOK;
  runScriptsAt(0); runScriptsAt(0);
  audioOK = _soundsStarted == soundCountBefore + 1 && _lastSound == 3 && _mixer->isSoundHandleActive(_soundHandle) && audioOK;
  runScriptsAt(150); runScriptsAt(500);
  clickAt(600,375); runScriptsAt(0); runScriptsAt(0);
  audioOK = _lastSound == 6 && _soundsStarted == soundCountBefore + 2 && audioOK;
  runScriptsAt(149); audioOK = _runner.clicksBlocked() && audioOK;
  runScriptsAt(150); runScriptsAt(1449);
  audioOK = _lastSound == 6 && audioOK;
  runScriptsAt(1450);
  audioOK = _lastSound == 2 && _soundsStarted == soundCountBefore + 3 && audioOK;
  Script missing; Command sound; sound.opcode = 9; sound.args.push_back(899); missing.push_back(sound);
  audioOK = !_runner.canRun(missing, true) && audioOK;
  audioOK = loadPlace(103) && !_mixer->isSoundHandleActive(_soundHandle) && audioOK;
  ConfMan.setBool("astronomica_audio", false);
  ConfMan.setBool("astronomica_sprite_input", false);
  debug("Astronomica audio verification: %s (P510 PCM, original clicks S3/S6/S2, replacement, missing target, scene stop)", audioOK ? "PASS" : "FAIL");
  scriptsOK = audioOK && scriptsOK;
'''
s=s.replace(anchor,test+anchor);p.write_text(s)
for p in r.iterdir(): shutil.copy2(p,Path('work/fresh-20260913/scummvm/engines/astronomica')/p.name)
