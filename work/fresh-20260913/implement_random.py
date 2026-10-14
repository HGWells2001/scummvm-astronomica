from pathlib import Path
import shutil
r=Path('outputs/astronomica-cleanroom/engine/astronomica')
p=r/'script.h';s=p.read_text().replace('_executed(0)', '_executed(0), _randomState(1)').replace(' void resetGlobals();', ' void resetGlobals();\n void seedRandom(uint16 seed) { _randomState = seed; }\n uint16 random15();').replace(' uint _executed;', ' uint _executed;\n uint32 _randomState;');p.write_text(s)
p=r/'script.cpp';s=p.read_text().replace('void ScriptRunner::resetGlobals()', '''uint16 ScriptRunner::random15() {
 // ASTRO.EXE 1:0b6b, including the 32-bit multiply helper at 1:0b3c.
 _randomState = _randomState * 0x015a4e35U + 1;
 return uint16((_randomState >> 16) & 0x7fff);
}
void ScriptRunner::resetGlobals()''')
s=s.replace('c.opcode == 33 || c.opcode == 46)', 'c.opcode == 33 || c.opcode == 40 || c.opcode == 46)')
s=s.replace('  case 33:', '''  case 40:
   // Original bounds and width are signed 16-bit. Admit the non-wrapping,
   // nonnegative subset; the result is zero-extended by the handler.
   if (c.args.size() != 4 || c.args[0] < 0 || c.args[0] > 1 || c.args[1] < 0 || c.args[1] >= 100 || c.args[2] < 0 || c.args[3] > 32767 || c.args[3] < c.args[2] || c.args[3] - c.args[2] >= 32767) return false;
   break;
  case 33:''',1)
s=s.replace('  } else if (c.opcode == 33) {', '''  } else if (c.opcode == 40) {
   const uint32 width = uint32(c.args[3] - c.args[2] + 1);
   _values[c.args[0]][c.args[1]] = c.args[2] + (uint32(random15()) * width) / 32768;
  } else if (c.opcode == 33) {''');p.write_text(s)
p=r/'conditions_test.cpp';s=p.read_text().replace('bool verifyConditions() {', '''static bool verifyRandomConditions() {
 ScriptRunner vm;
 const uint16 expected[] = {346,130,10982,1090,11656,7117,17595,6415,22948,31126,9004,14558};
 vm.seedRandom(1);
 for (uint i = 0; i < ARRAYSIZE(expected); ++i) if (vm.random15() != expected[i]) return false;
 for (int scope = 0; scope < 2; ++scope) {
  vm.seedRandom(1); vm.defineValue(scope,0,99); vm.defineValue(1-scope,0,88);
  Command c; c.opcode = 40; c.delay = 0;
  c.args.push_back(scope); c.args.push_back(0); c.args.push_back(1); c.args.push_back(3);
  Script s; s.push_back(c);
  const int values[] = {1,1,2,1,2,1,2,1,3,3,1,2};
  for (uint i = 0; i < ARRAYSIZE(values); ++i) {
   if (!vm.enqueue(s,0)) return false;
   vm.tick(0);
   if (!valueIs(vm,scope,0,values[i]) || !valueIs(vm,1-scope,0,88)) return false;
  }
  // Invalid ranges neither consume RNG state nor partially assign values.
  vm.seedRandom(1); s[0].args[2] = 4;
  if (vm.start(s,0) || vm.random15() != 346) return false;
  s[0].args[2] = -1;
  if (vm.start(s,0)) return false;
  s[0].args[2] = 0; s[0].args[3] = 32767;
  if (vm.start(s,0)) return false;
  s[0].args[2] = 32767;
  if (!vm.start(s,0) || !valueIs(vm,scope,0,32767)) return false;
 }
 return true;
}
bool verifyConditions() {
 if (!verifyRandomConditions()) return false;''');p.write_text(s)
p=r/'astronomica.cpp';s=p.read_text().replace('#include "common/system.h"','#include "common/system.h"\n#include "common/random.h"')
s=s.replace(' // _CreateGame allocates', ' _runner.seedRandom(uint16(Common::RandomSource::generateNewSeed()));\n // _CreateGame allocates')
anchor='  // Full, unmodified P29 entry program:'
test='''  bool randomOK = loadPlace(510);
  Script randomCommand;
  for (uint i = 0; i < _scene.scripts[0].size(); ++i)
   if (_scene.scripts[0][i].opcode == 40) randomCommand.push_back(_scene.scripts[0][i]);
  _runner.seedRandom(1);
  const int expectedVariants[] = {1,1,2,1,2,1,2,1,3,3,1,2};
  randomOK = randomCommand.size() == 1 && randomOK;
  for (uint i = 0; i < ARRAYSIZE(expectedVariants); ++i) {
   randomOK = _runner.enqueue(randomCommand,0) && randomOK;
   runScriptsAt(0); int32 variant;
   randomOK = _runner.getValue(1,0,variant) && variant == expectedVariants[i] && randomOK;
  }
  _runner.seedRandom(1);
  randomOK = _runner.random15() == 346 && loadPlace(136) && _runner.random15() == 130 && randomOK;
  debug("Astronomica random verification: %s (original P510 range 1..3, 12 seeded draws, state survives scene load)", randomOK ? "PASS" : "FAIL");
  scriptsOK = randomOK && scriptsOK;
'''
s=s.replace(anchor,test+anchor);p.write_text(s)
for p in r.iterdir(): shutil.copy2(p,Path('work/fresh-20260913/scummvm/engines/astronomica')/p.name)
