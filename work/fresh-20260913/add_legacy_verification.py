from pathlib import Path
r=Path('outputs/astronomica-cleanroom/engine/astronomica');p=r/'legacy_save.h';s=p.read_text().replace('#include "common/array.h"','#include "common/array.h"\n#include "common/file.h"\n#include "common/fs.h"')
s=s.replace('\n}\n#endif', '''
enum LegacyFileResult { kLegacyMissing, kLegacyInvalid, kLegacyLoaded };
inline LegacyFileResult readLegacyDirectory(const Common::FSNode &directory, LegacySaveState &state) {
 for (const char *name : {"gamestat","GAMESTAT"}) {
  const Common::FSNode node = directory.getChild(name);
  if (!node.exists()) continue;
  Common::File file;
  return file.open(node) && readLegacySave(file,state) ? kLegacyLoaded : kLegacyInvalid;
 }
 return kLegacyMissing;
}
}
#endif''');p.write_text(s)
p=r/'astronomica.cpp';s=p.read_text();a=s.index(' const Common::FSNode directory(ConfMan.getPath("path"));');b=s.index('\n}\nbool AstronomicaEngine::restoreLegacyState',a)
s=s[:a]+''' LegacySaveState candidate;
 const LegacyFileResult result = readLegacyDirectory(Common::FSNode(ConfMan.getPath("path")),candidate);
 if (result == kLegacyLoaded && validateLegacyDestination(candidate)) {
  _legacyState = candidate; _legacyAvailable = true;
 } else if (result != kLegacyMissing) warning("Astronomica: original GAMESTAT is invalid or cannot be restored without missing scene/clock state");'''+s[b:]
mark='bool AstronomicaEngine::verifyHelp() {'
method='''bool AstronomicaEngine::verifyLegacySaves() {
 const bool oldChecked = _legacyChecked, oldAvailable = _legacyAvailable;
 const LegacySaveState oldLegacy = _legacyState; const uint oldCompleted = _puzzlesCompleted;
 bool ok = true;
 auto parse = [](const Common::String &text, LegacySaveState &state) {
  Common::MemoryReadStream stream((const byte *)text.c_str(),text.size()); return readLegacySave(stream,state);
 };
 auto hash = [](const LegacySaveState &state) {
  uint32 h = (2166136261U ^ state.place)*16777619U; h = (h ^ state.completed)*16777619U;
  for (int32 value : state.globals) h = (h ^ uint32(value))*16777619U; return h;
 };
 // Expected words were obtained by executing the original writer/reader.
 struct Original { uint place, completed; uint32 hash; };
 const Original originals[] = {{117,12,0xd96ac188U},{523,31,0xb7b0beebU},{524,40,0xc7df18fdU},{523,0,0x637eb45aU},{1,0,0xc0379758U}};
 for (const Original &original : originals) for (const char *separator : {"\\n","\\r\\n"," \\t"}) {
  Common::String text = Common::String::format("%u%s%u%s",original.place,separator,original.completed,separator);
  for (uint i = 0; i < 100; ++i) text += Common::String::format("%d%s",int32(i*0x01020304U ^ 0xa5a5a5a5U),separator);
  LegacySaveState state; ok = parse(text,state) && hash(state) == original.hash && ok;
 }
 LegacySaveState initial; initial.place = 103; initial.completed = 7; initial.globals[99] = 1234;
 Common::String valid = "103\\n7\\n";
 for (uint i = 0; i < 100; ++i) valid += Common::String::format("%d\\n",initial.globals[i]);
 // Truncation at each token boundary cannot silently produce partial state.
 uint boundary = 0;
 for (uint count = 0; count < 102; ++count) {
  LegacySaveState state = initial;
  ok = !parse(valid.substr(0,boundary),state) && hash(state) == hash(initial) && ok;
  while (boundary < valid.size() && valid[boundary++] != '\\n') {}
 }
 for (const char *bad : {"","-","+","2147483648","-2147483649","12x","0x10","1e2"}) {
  LegacySaveState state = initial;
  ok = !parse(Common::String(bad)+valid.substr(3),state) && hash(state) == hash(initial) && ok;
 }
 for (const Common::String &bad : {valid+"0",valid+"garbage",Common::String('0',8193)}) {
  LegacySaveState state = initial; ok = !parse(bad,state) && hash(state) == hash(initial) && ok;
 }
 LegacySaveState extremes;
 Common::String signedText = "+103\\v+7\\f";
 for (uint i = 0; i < 100; ++i) signedText += (i%2 ? "-2147483648 " : "+2147483647 ");
 ok = parse(signedText,extremes) && extremes.globals[0] == 2147483647 && uint32(extremes.globals[1]) == 0x80000000U && ok;
 if (ConfMan.hasKey("astronomica_verify_legacy_directory")) {
  LegacySaveState fileState;
  ok = readLegacyDirectory(Common::FSNode(ConfMan.getPath("astronomica_verify_legacy_directory")),fileState) == kLegacyLoaded && hash(fileState) == hash(initial) && ok;
 }
 _runner.resetGlobals(); ok = loadPlace(117) && ok;
 _runner.defineValue(0,99,5678); _puzzlesCompleted = 9;
 for (uint destination : {0U,1U,26U,408U,409U,423U,437U,523U,538U,0xffffffffU}) {
  LegacySaveState unsupported = initial; unsupported.place = destination;
  ok = !restoreLegacyState(unsupported) && _place == 117 && _puzzlesCompleted == 9 && ok;
  int32 value = 0; ok = _runner.getValue(0,99,value) && value == 5678 && ok;
 }
 for (int mode : {1,2}) {
  LegacySaveState active = initial; active.globals[8] = 100; active.globals[60] = mode;
  ok = !restoreLegacyState(active) && _place == 117 && _puzzlesCompleted == 9 && ok;
 }
 ok = restoreLegacyState(initial) && _place == 103 && _puzzlesCompleted == 7 && !_runner.clicksBlocked() && ok;
 for (uint i = 0; i < 100; ++i) { int32 value = 0; ok = _runner.getValue(0,i,value) && value == initial.globals[i] && ok; }
 // Import can subsequently be saved and restored as a normal ScummVM slot.
 Common::MemoryWriteStreamDynamic native(DisposeAfterUse::YES);
 ok = saveGameStream(&native).getCode() == Common::kNoError && native.size() == 424 && ok;
 ok = loadPlace(117) && ok;
 Common::MemoryReadStream nativeInput(native.getData(),native.size());
 ok = loadGameStream(&nativeInput).getCode() == Common::kNoError && _place == 103 && _puzzlesCompleted == 7 && ok;
 // Original P1 flow: Start with a saved game opens the original choice;
 // its second button dispatches custom33 after its sound/delay.
 _legacyChecked = true; _legacyAvailable = true; _legacyState = initial;
 ok = loadPlace(1) && ok; _runner.enqueueStartup(_scene.scripts,0,true);
 for (uint32 now = 0; now <= 500; now += 10) runScriptsAt(now);
 int32 resume = 0; ok = _runner.getValue(1,1,resume) && resume == 1 && ok;
 const Sprite &start = _scene.sprites[2]; clickAtTime(start.renderX+10,start.renderY+10,510);
 for (uint32 now = 510; now <= 1500; now += 10) runScriptsAt(now);
 ok = _place == 1 && !_runner.clicksBlocked() && ok;
 const Sprite &button = _scene.sprites[1];
 ok = spriteAt(button.renderX+10,button.renderY+10) == 1 && _runner.canRun(button.click,true) && ok;
 clickAtTime(button.renderX+10,button.renderY+10,1510);
 for (uint32 now = 1510; now <= 5000 && _place == 1; now += 10) runScriptsAt(now);
 ok = _place == 103 && _puzzlesCompleted == 7 && !_runner.clicksBlocked() && !_runner.pendingCount() && ok;
 Script command; Command c; c.opcode = 23; for (int arg : {33,0,0,0,0,0}) c.args.push_back(arg); command.push_back(c);
 ok = !_runner.canRun(command,true) && ok;
 _legacyAvailable = false; ok = loadPlace(1) && !_runner.canRun(command,true) && ok;
 _legacyAvailable = true; ok = loadPlace(1) && _runner.canRun(command,true) && ok;
 command[0].args[1] = 1; ok = !_runner.canRun(command,true) && ok;
 _legacyChecked = oldChecked; _legacyAvailable = oldAvailable; _legacyState = oldLegacy;
 _puzzlesCompleted = oldCompleted; _runner.resetGlobals(); ok = loadPlace(103) && ok;
 debug("Astronomica legacy save verification: %s (15 original payloads, 102 token truncations, signed bounds, inactive import, native resave, original menu control, rejected active clocks/destinations)",ok ? "PASS" : "FAIL");
 return ok;
}
'''
s=s.replace(mark,method+mark)
branch=' if (ConfMan.hasKey("astronomica_verify_help")'
i=s.index(branch);s=s[:i]+''' if (ConfMan.hasKey("astronomica_verify_legacy") && ConfMan.getBool("astronomica_verify_legacy")) {
  ConfMan.setBool("astronomica_verify",true); ConfMan.setBool("astronomica_sprite_input",true);
  ConfMan.setBool("astronomica_entry_scripts",false);
  const bool ok = verifyLegacySaves();
  _background.free(); _screen.free(); quitGame();
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Legacy save verification failed");
 }
'''+s[i:];s=s.replace('  scriptsOK = verifyHelp() && scriptsOK;', '  scriptsOK = verifyLegacySaves() && scriptsOK;\n  scriptsOK = verifyHelp() && scriptsOK;');p.write_text(s)
for n in ('legacy_save.h','astronomica.h','astronomica.cpp','script.h','script.cpp'):
 Path('work/fresh-20260913/scummvm/engines/astronomica',n).write_bytes((r/n).read_bytes())
