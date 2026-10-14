from pathlib import Path
r=Path('outputs/astronomica-cleanroom/engine/astronomica');p=r/'astronomica.h';s=p.read_text().replace('#include "astronomica/help.h"','#include "astronomica/help.h"\n#include "astronomica/legacy_save.h"')
s=s.replace(' HelpBook _helpBook;', ''' LegacySaveState _legacyState;
 bool _legacyChecked = false, _legacyAvailable = false;
 void prepareLegacyResume();
 bool validateLegacyDestination(const LegacySaveState &state) const;
 bool restoreLegacyState(const LegacySaveState &state);
 bool verifyLegacySaves();
 HelpBook _helpBook;''')
s=s.replace('  // No legacy gamestat import/resume action yet; native loading is via F5.','  // Original text GAMESTAT is admitted only after complete validation.').replace('return {int32(_puzzlesCompleted),false,false,3000000};','return {int32(_puzzlesCompleted),_legacyAvailable,false,3000000};');p.write_text(s)
p=r/'script.h';s=p.read_text().replace(' void setHelpSupport(bool value)', ' void setLegacyResumeSupport(bool value) { _legacyResumeSupport = value; }\n void setHelpSupport(bool value)').replace('bool _worldMovieSupport = false, _helpSupport = false;', 'bool _worldMovieSupport = false, _helpSupport = false, _legacyResumeSupport = false;');p.write_text(s)
p=r/'script.cpp';s=p.read_text().replace('_worldMovieSupport = _helpSupport = false;', '_worldMovieSupport = _helpSupport = _legacyResumeSupport = false;')
s=s.replace('if (c.args[0] == 22) { if (!_helpSupport) return false; }', 'if (c.args[0] == 33) { if (!_legacyResumeSupport) return false; }\n    else if (c.args[0] == 22) { if (!_helpSupport) return false; }')
s=s.replace('  case 23:\n', '''  case 23:
   if (c.args.size() == 6 && c.args[0] == 33) {
    for (uint a = 1; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
''',1)
# Use the same external action path as help; the engine restores after dispatch.
s=s.replace('if (c.args[0] == 22)', 'if (c.args[0] == 22)',1)
# locate action-producing help branch
needle='c.args[0] == 22';print([s[max(0,i-30):i+160] for i in range(len(s)) if s.startswith(needle,i)])
p.write_text(s)
p=r/'astronomica.cpp';s=p.read_text();anchor='AstronomicaEngine::~AstronomicaEngine() {'
new='''bool AstronomicaEngine::validateLegacyDestination(const LegacySaveState &state) const {
 const uint place = state.place;
 if (!((place >= 27 && place <= 422) || (place > 437 && place <= 537)) || state.hasUnknownClock()) return false;
 Common::File file;
 const Common::Path path = ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%u/MEGAFILE.HYP",place)));
 if (!Common::FSNode(path).exists() || !file.open(Common::FSNode(path))) return false;
 Scene destination; ResourceReader reader(file);
 return reader.read(destination) && destination.mode == 1;
}
void AstronomicaEngine::prepareLegacyResume() {
 if (_legacyChecked) return; _legacyChecked = true; _legacyAvailable = false;
 // The port reads only the selected game's directory, never a drive-root or
 // process working-directory fallback. No original save is modified.
 const Common::FSNode directory(ConfMan.getPath("path"));
 for (const char *name : {"gamestat","GAMESTAT"}) {
  const Common::FSNode node = directory.getChild(name);
  if (!node.exists()) continue;
  Common::File file; LegacySaveState candidate;
  if (file.open(node) && readLegacySave(file,candidate) && validateLegacyDestination(candidate)) {
   _legacyState = candidate; _legacyAvailable = true;
  } else warning("Astronomica: original GAMESTAT is invalid or cannot be restored without missing scene/clock state");
  break;
 }
}
bool AstronomicaEngine::restoreLegacyState(const LegacySaveState &state) {
 if (!validateLegacyDestination(state)) return false;
 const ScriptRunner oldRunner = _runner; const uint oldCompleted = _puzzlesCompleted;
 for (int i = 0; i < 100; ++i) _runner.defineValue(0,i,state.globals[i]);
 _runner.resetVariantSequence(); _puzzlesCompleted = state.completed;
 if (!loadPlace(state.place)) { _runner = oldRunner; _puzzlesCompleted = oldCompleted; return false; }
 return true;
}
'''
s=s.replace(anchor,new+anchor)
s=s.replace(' _runner.setHelpSupport((place == 1 || place == 408) && ensureHelpBook());', ''' if (place == 1) prepareLegacyResume();
 _runner.setLegacyResumeSupport(place == 1 && _legacyAvailable);
 _runner.setHelpSupport((place == 1 || place == 408) && ensureHelpBook());''')
s=s.replace('  if (action.opcode == 23 && action.value == 22)', '''  if (action.opcode == 23 && action.value == 33) {
   if (_place == 1 && _legacyAvailable && restoreLegacyState(_legacyState)) return;
   warning("Astronomica: cannot resume original saved game"); continue;
  }
  if (action.opcode == 23 && action.value == 22)''')
p.write_text(s)
