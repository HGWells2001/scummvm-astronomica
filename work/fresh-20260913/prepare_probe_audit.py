"""Isolate the current real engine and add observation-only P522 diagnostics."""
from pathlib import Path
import hashlib,json,shutil
work=Path(__file__).resolve().parent;root=work.parents[1]
canonical=root/'outputs/astronomica-cleanroom/engine/astronomica'
stage=work/'p522-audit';stage.mkdir(exist_ok=False)
names=[stem+ext for stem in ('astronomica','script','sprites') for ext in ('.cpp','.h')]
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base={n:digest(canonical/n) for n in names}
for n in names:shutil.copyfile(canonical/n,stage/n)
(stage/'BASE.json').write_text(json.dumps(base,indent=2)+'\n')
p=stage/'astronomica.cpp';s=p.read_text()
a=s.index('bool AstronomicaEngine::verifyP522Puzzle() {');b=s.index('bool AstronomicaEngine::verifyP507Wheel()',a)
audit=s[a:b].replace('verifyP522Puzzle()','verifyProbeBoundaries()')
audit=audit.replace(' bool ok = verifyProbeMotion();',' uint observations = 0;\n bool ok = verifyProbeMotion();')
needle='  const uint completed = _puzzlesCompleted; uint32 now = 0;'
assert audit.count(needle)==1
audit=audit.replace(needle,needle+'''
  auto record = [&](const char *tag) {
   if (_place != 522 || _scene.sprites.size() != 18) return;
   int32 selector = -1,state = -1; _runner.getValue(1,0,selector); _runner.getValue(1,1,state);
   debug("Probe audit boundary: %u %d %s %u %d %d %d %d %u %u %u %u %d %d %d %d %d %d %u %u %u %u %u %u %08x %08x",
    observations,route,tag,now,_place,selector,state,_probe.year,uint(_probe.yearArmed),uint(_probe.specialHit),uint(_probe.flying),uint(_probe.expired),
    _probe.widths[0],_probe.heights[0],_probe.widths[1],_probe.heights[1],_probe.widths[2],_probe.heights[2],
    _runner.pendingCount(),uint(_runner.idle()),uint(_runner.scriptsIdle()),uint(_runner.clicksBlocked()),
    uint(_mixer->isSoundHandleActive(_soundHandle) && _lastSound != _loopSound),_puzzlesCompleted,screenRGBHash(_screen,480),screenRGBHash(_background,480));
   for (uint i = 0; i < 18; ++i) {
    Common::Array<uint32> words; p526SpriteWords(_scene.sprites[i],words);
    Common::String line = Common::String::format("Probe audit sprite: %u %u %u",observations,i,words.size());
    for (uint32 word : words) line += Common::String::format(" %d",int32(word));
    debug("%s",line.c_str());
   }
   ++observations;
  };
  record("before-startup");
''')
old='  auto step = [&]() { runScriptsAt(now); animateSpritesAt(now); now += 30; };'
new='''  auto step = [&]() {
   const int year = _probe.year; const bool armed = _probe.yearArmed,flying = _probe.flying,special = _probe.specialHit;
   int32 before = -1; _runner.getValue(1,1,before);
   runScriptsAt(now); animateSpritesAt(now); now += 30;
   if (_place != 522) { debug("Probe audit departure: %d %u %d %u",route,now,_place,_puzzlesCompleted); return; }
   int32 after = -1; _runner.getValue(1,1,after);
   if (now <= 360) record("startup-tick");
   else if (year != _probe.year || armed != _probe.yearArmed) record("calendar-edge");
   else if (flying != _probe.flying || special != _probe.specialHit || before != after) record("flight-transition");
  };'''
assert audit.count(old)==1;audit=audit.replace(old,new)
audit=audit.replace('clickAtTime(x,y,now); wait(600); return true;','clickAtTime(x,y,now); wait(600); record("after-control"); return true;')
audit=audit.replace('if (_probe.year == year && _scene.sprites[8].selectedFrame == month && !_runner.clicksBlocked()) return true;',
 'if (_probe.year == year && _scene.sprites[8].selectedFrame == month && !_runner.clicksBlocked()) { record("launch-window"); return true; }')
audit=audit.replace('== 11 && ok; wait(600);','== 11 && ok; wait(600); record("after-startup");')
audit=audit.replace('ok = _place == 522 && value == 0 && !_scene.sprites[16].visible && !_probe.flying && ok;',
 'ok = _place == 522 && value == 0 && !_scene.sprites[16].visible && !_probe.flying && ok; record("failed-return");')
audit=audit.replace('  return ok;','  return ok;')
audit=audit.replace(' return ok;\n}', ' debug("Astronomica probe boundary audit: %s (%u observations, four native routes; no save support)",ok ? "PASS" : "FAIL",observations);\n return ok;\n}')
s=s[:a]+audit+'\n'+s[a:]
needle=' if (ConfMan.hasKey("astronomica_verify_universe_saves")'
at=s.index(needle)
s=s[:at]+''' if (ConfMan.hasKey("astronomica_verify_probe_boundaries") && ConfMan.getBool("astronomica_verify_probe_boundaries")) {
  ConfMan.setBool("astronomica_verify",true);
  const bool ok = verifyProbeBoundaries();
  debug("Astronomica probe boundary result: %s",ok ? "PASS" : "FAIL");
  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"Probe boundary audit failed");
 }
'''+s[at:]
needle=' if (_place == 522 && _probe.expired) { changePlace(388); return; }'
assert s.count(needle)==1
s=s.replace(needle,' if (_place == 522 && _probe.expired) { debug("Probe audit expiry: %u %d %u",now,_probe.year,uint(_probe.expired)); changePlace(388); return; }')
p.write_text(s)
p=stage/'astronomica.h';s=p.read_text();needle=' bool verifyP522Puzzle();';assert s.count(needle)==1
p.write_text(s.replace(needle,' bool verifyProbeBoundaries();\n'+needle))
p=stage/'script.cpp';s=p.read_text();s=s.replace('#include "astronomica/script.h"','#include "astronomica/script.h"\n#include "common/debug.h"')
needle='  const int32 delay = p.script[p.index].delay;';assert s.count(needle)==1
s=s.replace(needle,needle+'''
  if (p.script[p.index].opcode == 41 && p.script[p.index].args.size() == 1 && !p.script[p.index].args[0] && delay == 200)
   debug("Probe audit poll: %u %u %d %u %u %u",now,p.since,delay,uint(int32(now-p.since) >= delay),count,p.index);
''')
p.write_text(s)
assert (work/'build_probe_audit.py').is_file(), 'Use the supplied isolated build helper'
assert base=={n:digest(canonical/n) for n in names}
print('Prepared six isolated current-engine sources; observations only, no serializer')
