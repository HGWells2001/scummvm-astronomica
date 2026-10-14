from pathlib import Path
root=Path('outputs/astronomica-cleanroom/engine/astronomica')
p=root/'script.h';s=p.read_text()
s=s.replace('// Clock values are supplied in original interpreter ticks. Conversion to wall\n// time is deliberately not assumed here. The explorer accepts only -1/0 delays.', '// Clock values are milliseconds: original MMSYSTEM ordinal 607, timeGetTime.')
s=s.replace(' void resetGlobals();',' void resetGlobals();\n void setPrograms(const Common::Array<Script> &scripts) { _programs = scripts; }')
s=s.replace('uint32 now);\n void tick', 'uint32 now, bool allowTimed = false);\n void tick')
s=s.replace(' Common::Array<Pending> _pending;', ' Common::Array<Script> _programs;\n Common::Array<Pending> _pending;')
s=s.replace('bool ready(const Script &script) const;', 'bool ready(const Script &script, bool allowTimed) const;')
p.write_text(s)
p=root/'script.cpp';s=p.read_text().replace(' _spriteTargets.clear();',' _spriteTargets.clear();\n _programs.clear();')
s=s.replace('bool ScriptRunner::ready(const Script &script) const {\n for', '''bool ScriptRunner::ready(const Script &root, bool allowTimed) const {
 // Validate the entire reachable graph, including cycles, before any effect.
 Common::Array<const Script *> work;
 Common::Array<bool> visited; visited.resize(_programs.size());
 for (uint i = 0; i < visited.size(); ++i) visited[i] = false;
 work.push_back(&root);
 for (uint w = 0; w < work.size(); ++w) {
 const Script &script = *work[w];
 if (!supports(script, allowTimed)) return false;
 for''')
s=s.replace('  const Command &c = script[i];\n  if (c.opcode == 7', '''  const Command &c = script[i];
  if (c.opcode == 41) {
   const uint target = uint(c.args[0]);
   if (target >= _programs.size() || _programs[target].empty()) return false;
   // _pend_command copies the template timestamp. Positive first delays need
   // template timestamp tracking; reject them until that lifecycle is decoded.
   if (_programs[target][0].delay > 0) return false;
   if (!visited[target]) { visited[target] = true; work.push_back(&_programs[target]); }
  }
  if (c.opcode == 7''',1)
s=s.replace(' return true;\n}\nbool ScriptRunner::supports', ' }\n return true;\n}\nbool ScriptRunner::supports',1)
s=s.replace('  case 16: case 17:', '  case 41:\n   if (c.args.size() != 1 || c.args[0] < 0 || c.args[0] > 32767) return false;\n   break;\n  case 16: case 17:',1)
s=s.replace('!ready(script)', '!ready(script, allowTimed)')
s=s.replace('uint ScriptRunner::enqueueStartup(const Common::Array<Script> &scripts, uint32 now)', 'uint ScriptRunner::enqueueStartup(const Common::Array<Script> &scripts, uint32 now, bool allowTimed)')
s=s.replace('if (enqueue(scripts[i], now))', 'if (enqueue(scripts[i], now, allowTimed))')
s=s.replace('  } else if (c.opcode == 42) {', '''  } else if (c.opcode == 41) {
   // 15:118b indexes the zero-based command table and calls _pend_command.
   // Appending, rather than executing recursively, preserves queue ordering.
   Pending p; p.script = _programs[c.args[0]]; p.index = 0; p.since = now;
   _pending.push_back(p);
  } else if (c.opcode == 42) {''')
# Add independent scheduling/graph-rejection regression checks.
s=s.replace(' return vm.popAction(action) && action.value == 126 && !vm.pendingCount();', ''' if (!vm.popAction(action) || action.value != 126 || vm.pendingCount()) return false;
 Script loop; Command call; call.opcode = 41; call.args.push_back(0); call.delay = 600;
 loop.push_back(nop); loop.push_back(call);
 Common::Array<Script> programs; programs.push_back(loop); vm.setPrograms(programs);
 if (!vm.enqueue(loop, 100, true)) return false;
 vm.tick(100); uint before = vm.executedCount();
 vm.tick(699); if (vm.executedCount() != before) return false;
 vm.tick(700); if (vm.executedCount() != before + 1 || vm.pendingCount() != 1) return false;
 vm.tick(700); if (vm.executedCount() != before + 2 || vm.pendingCount() != 1) return false;
 vm.clear();
 // An unsupported command in a called script must reject the caller atomically.
 programs[0][0].opcode = 999; vm.setPrograms(programs);
 before = vm.executedCount();
 if (vm.enqueue(loop, 0, true) || vm.executedCount() != before || vm.pendingCount()) return false;
 programs[0] = loop; programs[0][1].args[0] = 1; vm.setPrograms(programs);
 if (vm.enqueue(loop, 0, true)) return false;
 programs[0] = loop; programs[0][0].delay = 10; vm.setPrograms(programs);
 return !vm.enqueue(loop, 0, true);''')
p.write_text(s)
p=root/'astronomica.h';s=p.read_text().replace(' void runScripts();',' uint32 scriptClock() const;\n void runScripts();\n void runScriptsAt(uint32 now);');p.write_text(s)
p=root/'astronomica.cpp';s=p.read_text().replace(' _runner.setSpriteTargets(targets);',' _runner.setSpriteTargets(targets);\n _runner.setPrograms(_scene.scripts);')
s=s.replace('_runner.enqueue(one, 0)', '_runner.enqueue(one, scriptClock(), true)').replace('_runner.enqueueStartup(_scene.scripts, 0);', '_runner.enqueueStartup(_scene.scripts, scriptClock(), true);',1).replace('_runner.enqueue(r.click, 0)', '_runner.enqueue(r.click, scriptClock(), true)')
s=s.replace('void AstronomicaEngine::runScripts() {\n // Only -1/0 delays are admitted by enqueue, so no tick-to-ms assumption.\n _runner.tick(0);', '''uint32 AstronomicaEngine::scriptClock() const {
 if (ConfMan.hasKey("astronomica_verify") && ConfMan.getBool("astronomica_verify")) return 0;
 return _system->getMillis();
}
void AstronomicaEngine::runScripts() { runScriptsAt(scriptClock()); }
void AstronomicaEngine::runScriptsAt(uint32 now) {
 _runner.tick(now);''')
anchor='  // Global values survive ordinary scene loads and reset on entry to P1.'
test='''  // Full, unmodified P29 entry program: repeated show/hide and self-call.
  bool timerOK = loadPlace(29) && _scene.scripts.size() == 1;
  timerOK = _runner.enqueueStartup(_scene.scripts, 0, true) == 1 && timerOK;
  runScriptsAt(0); runScriptsAt(0); runScriptsAt(0);
  timerOK = _scene.sprites[1].visible && _runner.pendingCount() == 1 && timerOK;
  const uint beforeTimer = _runner.executedCount();
  runScriptsAt(599);
  timerOK = _runner.executedCount() == beforeTimer && timerOK;
  runScriptsAt(600); // queues the entry; does not run it during this pass
  timerOK = _scene.sprites[1].visible && _runner.pendingCount() == 1 && timerOK;
  runScriptsAt(600); runScriptsAt(600); runScriptsAt(600);
  timerOK = !_scene.sprites[1].visible && screenRGBHash(_screen) == (rgb565 ? 0xf46c822eU : 0xa8aa76a9U) && timerOK;
  runScriptsAt(1199);
  timerOK = !_scene.sprites[1].visible && timerOK;
  runScriptsAt(1200); runScriptsAt(1200); runScriptsAt(1200); runScriptsAt(1200);
  timerOK = _scene.sprites[1].visible && _runner.pendingCount() == 1 && screenRGBHash(_screen) == (rgb565 ? 0x97802e24U : 0xca004a3bU) && timerOK;
  debug("Astronomica timer verification: %s (P29 complete original script, 599/600/1199/1200 ms)", timerOK ? "PASS" : "FAIL");
  scriptsOK = timerOK && scriptsOK;
'''
s=s.replace(anchor,test+anchor);p.write_text(s)
import shutil
for p in root.iterdir(): shutil.copy2(p,Path('work/fresh-20260913/scummvm/engines/astronomica')/p.name)
