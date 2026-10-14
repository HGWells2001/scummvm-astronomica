from pathlib import Path
import shutil
r=Path('outputs/astronomica-cleanroom/engine/astronomica')
p=r/'script.cpp';s=p.read_text().replace('if (c.opcode == 31 || c.opcode == 32 || c.opcode == 46)', 'if (c.opcode == 31 || c.opcode == 32 || c.opcode == 33 || c.opcode == 46)')
s=s.replace('  case 31: case 32: case 46:', '''  case 33:
   if (c.args.size() != 4 || c.args[0] < 0 || c.args[0] > 1 || c.args[1] < 0 || c.args[1] >= 100 || c.args[2] < 0 || c.args[2] > 30 || (c.args[3] != 0 && c.args[3] != 1)) return false;
   break;
  case 31: case 32: case 46:''')
s=s.replace('  } else if (c.opcode == 46) {', '''  } else if (c.opcode == 33) {
   // Original uses pow(2, bit), then OR for set, or TEST + SUB for clear.
   // For admitted bits 0..30 this is exact and has no floating conversion.
   const uint32 mask = uint32(1) << c.args[2];
   uint32 value = uint32(_values[c.args[0]][c.args[1]]);
   if (c.args[3] == 1) value |= mask;
   else if (value & mask) value -= mask;
   _values[c.args[0]][c.args[1]] = int32(value);
  } else if (c.opcode == 46) {''');p.write_text(s)
p=r/'conditions_test.cpp';s=p.read_text();s=s.replace('bool verifyConditions() {', '''static bool verifyBitConditions() {
 for (int scope = 0; scope < 2; ++scope) {
  ScriptRunner vm; vm.defineValue(scope,99,int32(0x80000001U));
  vm.defineValue(1-scope,99,17);
  Command c; c.opcode = 33; c.delay = 0;
  c.args.push_back(scope); c.args.push_back(99); c.args.push_back(30); c.args.push_back(1);
  Script s; s.push_back(c);
  if (!vm.enqueue(s,0) || !valueIs(vm,scope,99,int32(0x80000001U))) return false;
  vm.tick(0);
  if (!valueIs(vm,scope,99,int32(0xc0000001U))) return false;
  if (!vm.start(s,0) || !valueIs(vm,scope,99,int32(0xc0000001U))) return false;
  s[0].args[3] = 0;
  if (!vm.start(s,0) || !valueIs(vm,scope,99,int32(0x80000001U))) return false;
  if (!vm.start(s,0) || !valueIs(vm,scope,99,int32(0x80000001U))) return false;
  s[0].args[2] = 0;
  if (!vm.start(s,0) || !valueIs(vm,scope,99,int32(0x80000000U)) || !valueIs(vm,1-scope,99,17)) return false;
  // A valid assignment preceding an invalid bit operation must not execute.
  s[0].args[2] = 31;
  Script invalid; invalid.push_back(command(32,scope,99,7)); invalid.push_back(s[0]);
  if (vm.start(invalid,0) || !valueIs(vm,scope,99,int32(0x80000000U))) return false;
  invalid[1].args[2] = -1;
  if (vm.start(invalid,0)) return false;
  invalid[1].args[2] = 0; invalid[1].args[1] = 100;
  if (vm.start(invalid,0)) return false;
 }
 return true;
}
bool verifyConditions() {
 if (!verifyBitConditions()) return false;''');p.write_text(s)
p=r/'astronomica.cpp';s=p.read_text();anchor='  // Full, unmodified P29 entry program:'
test='''  bool bitsOK = loadPlace(511) && _scene.scripts.size() > 3;
  _runner.defineValue(1,5,6); _runner.defineValue(0,5,123);
  uint bitOperations = 0;
  if (bitsOK) for (uint i = 0; i < _scene.scripts[3].size(); ++i) {
   const Command &c = _scene.scripts[3][i];
   if (c.opcode != 33) continue;
   Script one; one.push_back(c);
   bitsOK = _runner.enqueue(one,0) && bitsOK;
   runScriptsAt(0);
   int32 value;
   bitsOK = _runner.getValue(1,5,value) && value == (bitOperations == 0 ? 7 : 6) && bitsOK;
   ++bitOperations;
  }
  int32 globalBits;
  bitsOK = bitOperations == 4 && _runner.getValue(0,5,globalBits) && globalBits == 123 && bitsOK;
  debug("Astronomica bit verification: %s (original P511 commands: 6/7/6/6/6, unrelated bits and global preserved)", bitsOK ? "PASS" : "FAIL");
  scriptsOK = bitsOK && scriptsOK;
'''
s=s.replace(anchor,test+anchor);p.write_text(s)
for p in r.iterdir(): shutil.copy2(p,Path('work/fresh-20260913/scummvm/engines/astronomica')/p.name)
