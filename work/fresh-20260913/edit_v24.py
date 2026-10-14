from pathlib import Path
import json
p=Path('outputs/astronomica-cleanroom/engine/astronomica');rows=json.loads(Path('outputs/astronomica-cleanroom/evidence/success-map.json').read_text())
f=p/'script.h';s=f.read_text().replace('void setSuccessHandler(SuccessHandler *handler) { _successHandler = handler; }','static int successGlobalForPlace(int place);\n void setSuccessHandler(SuccessHandler *handler, int place) { _successHandler = handler; _successGlobal = successGlobalForPlace(place); }');s=s.replace(' SuccessHandler *_successHandler = nullptr;', ' SuccessHandler *_successHandler = nullptr;\n int _successGlobal = -1;');f.write_text(s)
f=p/'script.cpp';s=f.read_text().replace('namespace Astronomica {','namespace Astronomica {\nint ScriptRunner::successGlobalForPlace(int place) {\n switch (place) {\n'+''.join(f" case {r['scene']}: return {r['global_id']};\n" for r in rows)+' default: return -1;\n }\n}\n',1);s=s.replace(' _successHandler = nullptr;', ' _successHandler = nullptr; _successGlobal = -1;');s=s.replace('(!_successHandler || !_known[0][27])','(!_successHandler || _successGlobal < 0 || !_known[0][_successGlobal])');s=s.replace('// Admit only the original P511 success operation; scene support is','// Admit the original common success operation; scene support is');s=s.replace('// Original 4:57c6: global offset 0x76 = 0x0a + 27*4.', '// Original per-scene dispatch uses a DWORD within the global array.');s=s.replace('_values[0][27]', '_values[0][_successGlobal]');f.write_text(s)
f=p/'astronomica.cpp';s=f.read_text().replace('if (_place == 511 && ConfMan.hasKey("astronomica_audio")', 'if (ScriptRunner::successGlobalForPlace(_place) >= 0 && ConfMan.hasKey("astronomica_audio")');s=s.replace('_runner.setSuccessHandler(this);','_runner.setSuccessHandler(this,_place);');anchor='  // Full, unmodified P29 entry program: repeated show/hide and self-call.'
test='''  ConfMan.setBool("astronomica_audio", true);
  bool multiSuccessOK = true;
  const int successPlaces[] = {PLACES};
  const int successGlobals[] = {GLOBALS};
  for (uint i = 0; i < ARRAYSIZE(successPlaces); ++i) {
   multiSuccessOK = loadPlace(successPlaces[i]) && multiSuccessOK;
   for (int g = 0; g < 100; ++g) _runner.defineValue(0,g,-2);
   const uint countBefore = _puzzlesCompleted, soundsBefore = _soundsStarted;
   // Nonzero flags normalize to 1 without replaying or incrementing.
   multiSuccessOK = _runner.start(originalSuccess,0,true) && multiSuccessOK;
   for (int g = 0; g < 100; ++g) {
    int32 actual = 0;
    multiSuccessOK = _runner.getValue(0,g,actual) && actual == (g == successGlobals[i] ? 1 : -2) && multiSuccessOK;
   }
   multiSuccessOK = _puzzlesCompleted == countBefore && _soundsStarted == soundsBefore && multiSuccessOK;
  }
  // A different puzzle executes its own original success command with sound.
  multiSuccessOK = loadPlace(517) && multiSuccessOK;
  Script success517;
  for (uint s = 0; s < _scene.scripts.size(); ++s) for (uint c = 0; c < _scene.scripts[s].size(); ++c)
   if (_scene.scripts[s][c].opcode == 23 && _scene.scripts[s][c].args[0] == 25 && success517.empty()) success517.push_back(_scene.scripts[s][c]);
  _runner.defineValue(0,33,0);
  const uint count517 = _puzzlesCompleted;
  multiSuccessOK = success517.size() == 1 && _runner.start(success517,0,true) &&
   _runner.getValue(0,33,completionFlag) && completionFlag == 1 && _puzzlesCompleted == count517+1 && _lastSound == 912 && multiSuccessOK;
  // P506 and variants P531..535 share global 23; changing scene must preserve it.
  multiSuccessOK = loadPlace(506) && multiSuccessOK; _runner.defineValue(0,23,1);
  multiSuccessOK = loadPlace(533) && _runner.start(originalSuccess,0,true) && _puzzlesCompleted == count517+1 && multiSuccessOK;
  const int specialPlaces[] = {513,529,530};
  for (uint i = 0; i < ARRAYSIZE(specialPlaces); ++i)
   multiSuccessOK = loadPlace(specialPlaces[i]) && !_runner.canRun(originalSuccess,true) && multiSuccessOK;
  debug("Astronomica multi-puzzle success verification: %s (29 scene mappings, 100 globals checked each, original P517 sound/count, shared P506/P533 state, exceptions rejected)", multiSuccessOK ? "PASS" : "FAIL");
  scriptsOK = multiSuccessOK && scriptsOK;
  _runner.resetGlobals();
  ConfMan.setBool("astronomica_audio", false);
'''.replace('PLACES',','.join(str(r['scene']) for r in rows)).replace('GLOBALS',','.join(str(r['global_id']) for r in rows))
s=s.replace(anchor,test+anchor);f.write_text(s)
import shutil
for f in p.iterdir():
 if f.is_file(): shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
