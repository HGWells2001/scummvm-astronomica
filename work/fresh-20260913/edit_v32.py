from pathlib import Path
import shutil
out=Path('outputs/astronomica-cleanroom');engine=out/'engine/astronomica'
p=engine/'script.h';s=p.read_text().replace('void setPrograms(const Common::Array<Script> &scripts) { _programs = scripts; }','void setPrograms(const Common::Array<Script> &scripts, uint32 loadedAt = 0) { _programs = scripts; _programLoadedAt = loadedAt; }').replace('Common::Array<Script> _programs;','Common::Array<Script> _programs;\n uint32 _programLoadedAt = 0;');p.write_text(s)
p=engine/'script.cpp';s=p.read_text();a=s.index('   // _pend_command copies the template timestamp.');b=s.index('   if (!visited[target])',a);s=s[:a]+s[b:]
s=s.replace('if (!scripts[i].empty() && scripts[i][0].delay <= 0 && enqueue(scripts[i], now, allowTimed)) ++accepted;', 'if (!scripts[i].empty() && enqueue(scripts[i], _programLoadedAt, allowTimed)) ++accepted;')
s=s.replace('Pending p; p.script = _programs[c.args[0]]; p.index = 0; p.since = now;', '// _copy_command 15:1ad4 copies the timestamp initialized at 9:340f.\n   // Calling a template does not restart its first-command timer.\n   Pending p; p.script = _programs[c.args[0]]; p.index = 0; p.since = _programLoadedAt;')
s=s.replace(' programs[0] = loop; programs[0][0].delay = 10; vm.setPrograms(programs);\n if (vm.enqueue(loop,0,true)) return false;', ''' // Delayed template heads retain the load epoch on startup and each call.
 Script delayed; Command delayedGo = go; delayedGo.delay = 3500; delayed.push_back(delayedGo);
 programs.clear(); programs.push_back(delayed); vm.setPrograms(programs,1000);
 if (vm.enqueueStartup(programs,2000,true) != 1) return false;
 vm.tick(4499); if (vm.popAction(action)) return false;
 vm.tick(4500); if (!vm.popAction(action) || action.value != 126 || vm.pendingCount()) return false;
 Script invoke; Command invokeCommand = call; invokeCommand.delay = 0; invoke.push_back(invokeCommand);
 if (!vm.start(invoke,9000,true) || vm.popAction(action)) return false;
 vm.tick(9000); if (!vm.popAction(action) || action.value != 126 || vm.pendingCount()) return false;
 if (!vm.start(invoke,10000,true)) return false;
 vm.tick(10000); if (!vm.popAction(action) || vm.pendingCount()) return false;
 // A new scene resets the epoch; unsigned clock wrap remains well-defined.
 vm.setPrograms(programs,0xfffffff0U);
 if (vm.enqueueStartup(programs,0xfffffff0U,false) != 0 || vm.pendingCount()) return false;
 if (vm.enqueueStartup(programs,0xfffffff0U,true) != 1) return false;
 vm.tick(3483); if (vm.popAction(action)) return false;
 vm.tick(3484); if (!vm.popAction(action) || vm.pendingCount()) return false;
 vm.setPrograms(programs,20000);
 if (vm.enqueueStartup(programs,25000,true) != 1) return false;
 vm.tick(25000); if (!vm.popAction(action) || vm.pendingCount()) return false;''')
p.write_text(s)
p=engine/'astronomica.cpp';s=p.read_text().replace('_runner.setPrograms(_scene.scripts);','_runner.setPrograms(_scene.scripts, scriptClock());')
marker='  // P511: solve from the original initial conditions using only hit-tested clicks.'
test='''  // Original P509 delayed entry: first command becomes eligible after 3500 ms.
  bool delayedEntryOK = loadPlace(509) && _scene.scripts.size() == 6 && _scene.scripts[0][0].delay == 3500;
  Common::Array<Script> delayedEntry; delayedEntry.push_back(_scene.scripts[0]);
  delayedEntryOK = _runner.enqueueStartup(delayedEntry,0,true) == 1 && delayedEntryOK;
  int32 enabled = -1;
  runScriptsAt(3499);
  delayedEntryOK = _runner.getValue(1,15,enabled) && enabled == 0 && _runner.pendingCount() == 1 && delayedEntryOK;
  runScriptsAt(3500);
  delayedEntryOK = _runner.getValue(1,15,enabled) && enabled == 1 && !_runner.pendingCount() && delayedEntryOK;
  debug("Astronomica delayed entry verification: %s (original P509 script 0, 3499/3500 ms)",delayedEntryOK ? "PASS" : "FAIL");
  scriptsOK = delayedEntryOK && scriptsOK;
'''
assert marker in s;s=s.replace(marker,test+marker);p.write_text(s)
for f in engine.iterdir():shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
