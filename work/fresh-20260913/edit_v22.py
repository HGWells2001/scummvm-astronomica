from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica')
f=p/'script.h';s=f.read_text().replace(' struct Action {',' struct SuccessHandler { virtual ~SuccessHandler() {} virtual uint32 onPuzzleSuccess(uint32 now) = 0; };\n void setSuccessHandler(SuccessHandler *handler) { _successHandler = handler; }\n struct Action {');s=s.replace(' uint32 _randomState;', ' uint32 _randomState;\n SuccessHandler *_successHandler = nullptr;');f.write_text(s)
f=p/'script.cpp';s=f.read_text().replace(' _soundTargets.clear();', ' _soundTargets.clear();\n _successHandler = nullptr;');s=s.replace('  if (c.opcode == 39) {', '  if (c.opcode == 23 && (!_successHandler || !_known[0][27])) return false;\n  if (c.opcode == 39) {',1);s=s.replace('  case 25: case 26:', '''  case 23:
   // Admit only the original P511 success operation; scene support is
   // supplied by the engine, never inferred from the command alone.
   if (c.args.size() != 6 || c.args[0] != 25) return false;
   for (uint a = 1; a < 6; ++a) if (c.args[a] != 0) return false;
   break;
  case 25: case 26:''');s=s.replace('  if (c.opcode == 31) {\n   const int32', '''  if (c.opcode == 23) {
   // Original 4:57c6: global offset 0x76 = 0x0a + 27*4.
   // Sound and counter happen before the flag store, only when it was zero.
   if (_values[0][27] == 0) now = _successHandler->onPuzzleSuccess(now);
   _values[0][27] = 1;
  } else if (c.opcode == 31) {
   const int32''');f.write_text(s)
f=p/'astronomica.h';s=f.read_text().replace('class AstronomicaEngine : public Engine {','class AstronomicaEngine : public Engine, public ScriptRunner::SuccessHandler {');s=s.replace(' bool verifyAudio();',' bool verifyAudio();\n uint32 onPuzzleSuccess(uint32 now) override;\n uint32 _puzzlesCompleted = 0;');f.write_text(s)
f=p/'astronomica.cpp';s=f.read_text().replace('if (id < 0 || id >= 900) return nullptr;', 'if (id < 0 || (id >= 900 && id != 912)) return nullptr;');s=s.replace('Common::String::format("PLACES/P%d/S%d.WAV", _place, id)', '(id == 912 ? Common::String("SOUNDS/S12.WAV") : Common::String::format("PLACES/P%d/S%d.WAV", _place, id))');s=s.replace(' _runner.setSoundTargets(targets);',''' _runner.setSoundTargets(targets);
 if (_place == 511 && ConfMan.hasKey("astronomica_audio") && ConfMan.getBool("astronomica_audio")) {
  Common::File successFile;
  const Common::Path successPath = ConfMan.getPath("path").join(Common::Path("SOUNDS/S12.WAV"));
  int size, rate; byte flags; uint16 type;
  if (successFile.open(Common::FSNode(successPath)) && Audio::loadWAVFromStream(successFile, size, rate, flags, &type) && type == 1)
   _runner.setSuccessHandler(this);
 }
''');s=s.replace('bool AstronomicaEngine::verifyAudio() {', '''uint32 AstronomicaEngine::onPuzzleSuccess(uint32 now) {
 // Apply preceding visual/audio effects before the original synchronous sound.
 applyScriptActions(now);
 const uint32 started = _system->getMillis();
 if (playSound(912,now)) {
  while (_mixer->isSoundHandleActive(_soundHandle) && !shouldQuit()) {
   Common::Event event;
   while (_system->getEventManager()->pollEvent(event))
    if (event.type == Common::EVENT_QUIT) quitGame();
   _system->delayMillis(5);
  }
 }
 ++_puzzlesCompleted; // Original _puzzle_successful increments DS:0153.
 return now + uint32(_system->getMillis() - started);
}
bool AstronomicaEngine::verifyAudio() {''');f.write_text(s)
import shutil
for f in p.iterdir():
 if f.is_file(): shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
