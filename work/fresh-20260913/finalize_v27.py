from pathlib import Path
import shutil
p=Path('outputs/astronomica-cleanroom/engine/astronomica')
f=p/'script.h';s=f.read_text().replace(' void setSoundTargets(', ' void setMissingSoundTarget(int id) { _missingSoundTarget = id; }\n void setSoundTargets(');s=s.replace(' Common::Array<bool> _soundTargets;', ' Common::Array<bool> _soundTargets;\n int _missingSoundTarget = -1;');f.write_text(s)
f=p/'script.cpp';s=f.read_text().replace(' _soundTargets.clear();', ' _missingSoundTarget = -1;\n _soundTargets.clear();');s=s.replace('if ((c.opcode == 9 || c.opcode == 27) && (', 'if ((c.opcode == 9 || c.opcode == 27) && !(c.opcode == 9 && c.args[0] == _missingSoundTarget) && (');f.write_text(s)
f=p/'astronomica.cpp';s=f.read_text().replace('if (!Common::FSNode(missing).exists()) targets[9] = true;', 'if (!Common::FSNode(missing).exists()) _runner.setMissingSoundTarget(9);');s=s.replace('if (!file->open(Common::FSNode(path))) { delete file; return nullptr; }', 'if (!Common::FSNode(path).exists() || !file->open(Common::FSNode(path))) { delete file; return nullptr; }');# assertion exception not admitted for looping
needle='   const uint32 completedBefore = _puzzlesCompleted;';s=s.replace(needle,'''   Script missingLoop; Command missingLoopCommand; missingLoopCommand.opcode = 27; missingLoopCommand.args.push_back(9); missingLoop.push_back(missingLoopCommand);
   answersOK = !_runner.canRun(missingLoop,true) && answersOK;
'''+needle);f.write_text(s)
for f in p.iterdir():
 if f.is_file(): shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
