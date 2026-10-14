// SPDX-License-Identifier: GPL-3.0-or-later
#include "astronomica/script.h"
namespace Astronomica {
static Command command(int op, int a = 0, int b = 0, int c = 0, int d = 0, int e = 0) {
 Command out; out.opcode = op; out.delay = -1;
 if (op == 31 || op == 32 || op == 46) {
  out.args.push_back(a); out.args.push_back(b); out.args.push_back(c);
  if (op == 31) { out.args.push_back(d); out.args.push_back(e); out.args.push_back(0); }
 }
 return out;
}
static bool valueIs(const ScriptRunner &vm, int scope, int id, int32 expected) {
 int32 value; return vm.getValue(scope, id, value) && value == expected;
}
static bool verifyBitConditions() {
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
static bool verifyRandomConditions() {
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
 for (int sourceScope = 0; sourceScope < 2; ++sourceScope) for (int targetScope = 0; targetScope < 2; ++targetScope) {
  ScriptRunner vm; Common::Array<Condition> declarations;
  Condition c; c.raw[0] = sourceScope; c.raw[1] = 0; c.raw[2] = 3;
  declarations.push_back(c); vm.loadLocalConditions(declarations);
  vm.defineValue(sourceScope,0,int32(0x80000002U)); vm.defineValue(targetScope,1,99);
  vm.seedRandom(1);
  Command pick; pick.opcode = 39;
  pick.args.push_back(sourceScope); pick.args.push_back(0); pick.args.push_back(targetScope); pick.args.push_back(1);
  Script s; s.push_back(pick);
  if (!vm.start(s,0) || !valueIs(vm,sourceScope,0,int32(0x80000003U)) || !valueIs(vm,targetScope,1,1)) return false;
  if (!vm.start(s,0) || !valueIs(vm,sourceScope,0,int32(0x80000007U)) || !valueIs(vm,targetScope,1,3)) return false;
  if (!vm.start(s,0) || !valueIs(vm,targetScope,1,3) || vm.random15() != 1090) return false;
  declarations[0].raw[2] = 32; vm.loadLocalConditions(declarations);
  vm.defineValue(sourceScope,0,0); vm.defineValue(targetScope,1,99); vm.seedRandom(1);
  if (vm.start(s,0) || vm.random15() != 346 || !valueIs(vm,targetScope,1,99)) return false;
 }
 if (!verifyRandomConditions()) return false;
 if (!verifyBitConditions()) return false;
 // Signed comparisons and inclusive range edges, in both original scopes.
 const int32 values[] = {int32(0x80000000U), -6, -5, -4, 4, 5, 6, 0x7fffffff};
 for (int scope = 0; scope < 2; ++scope) {
  for (int comparison = 0; comparison < 4; ++comparison) {
   for (uint i = 0; i < ARRAYSIZE(values); ++i) {
    ScriptRunner vm;
    vm.defineValue(scope, 0, values[i]); vm.defineValue(scope, 1, 0); vm.defineValue(scope, 2, 0);
    Script s;
    s.push_back(command(31, scope, 0, -5, 5, comparison));
    s.push_back(command(32, scope, 1, 11));
    s.push_back(command(42));
    s.push_back(command(32, scope, 2, 22));
    const bool expected = comparison == 0 ? values[i] == -5 : comparison == 1 ? values[i] < -5 : comparison == 2 ? values[i] > -5 : values[i] >= -5 && values[i] <= 5;
    if (!vm.start(s, 0) || !valueIs(vm, scope, 1, expected ? 11 : 0) || !valueIs(vm, scope, 2, 22)) return false;
   }
  }
 }
 // Original else form: the command following ELSE is another CONDITION.
 for (int input = 5; input <= 7; ++input) {
  ScriptRunner vm; vm.defineValue(1, 0, input); vm.defineValue(1, 1, 0); vm.defineValue(1, 2, 0);
  Script s;
  s.push_back(command(31, 1, 0, 5)); s.push_back(command(32, 1, 1, 11));
  s.push_back(command(45)); s.push_back(command(31, 1, 0, 6));
  s.push_back(command(32, 1, 1, 12)); s.push_back(command(42));
  s.push_back(command(32, 1, 2, 22));
  if (!vm.start(s, 0) || !valueIs(vm, 1, 1, input == 5 ? 11 : input == 6 ? 12 : 0) || !valueIs(vm, 1, 2, 22)) return false;
 }
 ScriptRunner vm; vm.defineValue(0, 0, 0x7fffffff); vm.defineValue(1, 0, 9);
 Script add; add.push_back(command(46, 0, 0, 1));
 if (!vm.start(add, 0) || !valueIs(vm, 0, 0, int32(0x80000000U)) || !valueIs(vm, 1, 0, 9)) return false;
 add[0].args[2] = -1;
 if (!vm.start(add, 0) || !valueIs(vm, 0, 0, 0x7fffffff)) return false;
 // Unknown state or an invalid comparison rejects the WHOLE sequence.
 Script invalid; invalid.push_back(command(32, 1, 0, 8)); invalid.push_back(command(31, 0, 99, 0));
 if (vm.start(invalid, 0) || !valueIs(vm, 1, 0, 9)) return false;
 invalid[1] = command(31, 1, 0, 0, 0, 4);
 if (vm.start(invalid, 0) || !valueIs(vm, 1, 0, 9)) return false;
 // A branch into delay=0 must yield before modifying its destination.
 Script delayed; delayed.push_back(command(31, 1, 0, 9));
 delayed.push_back(command(32, 1, 0, 10)); delayed[1].delay = 0;
 delayed.push_back(command(42));
 if (!vm.start(delayed, 0) || !valueIs(vm, 1, 0, 9) || vm.pendingCount() != 1) return false;
 vm.tick(0);
 if (!valueIs(vm, 1, 0, 10) || vm.pendingCount()) return false;
 // Scene declarations seed local values from field 3, never field 2.
 Common::Array<Condition> declarations;
 Condition local; local.raw[0] = 1; local.raw[1] = 2; local.raw[2] = 999; local.raw[3] = -17;
 declarations.push_back(local);
 Condition global = local; global.raw[0] = 0; global.raw[1] = 0;
 declarations.push_back(global);
 vm.loadLocalConditions(declarations);
 int32 value;
 if (!valueIs(vm, 1, 2, -17) || !valueIs(vm, 0, 0, 0x7fffffff) || vm.getValue(1, 0, value) || vm.defineValue(1, 100, 0)) return false;
 vm.resetGlobals();
 for (int id = 0; id < 100; ++id)
  if (!valueIs(vm, 0, id, 0)) return false;
 if (!valueIs(vm, 1, 2, -17)) return false;
 // Entry scripts defer even their first command; its delay is not ignored.
 Script entry; entry.push_back(command(32, 0, 0, 7));
 if (!vm.enqueue(entry, 100) || !valueIs(vm, 0, 0, 0)) return false;
 vm.tick(100);
 if (!valueIs(vm, 0, 0, 7)) return false;
 entry[0].args[2] = 8; entry[0].delay = 5;
 if (vm.enqueue(entry, 100) || !vm.enqueue(entry, 100, true)) return false;
 vm.tick(104);
 if (!valueIs(vm, 0, 0, 7)) return false;
 vm.tick(105);
 return valueIs(vm, 0, 0, 8) && !vm.pendingCount();
}
}
