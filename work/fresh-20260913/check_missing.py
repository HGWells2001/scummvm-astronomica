from pathlib import Path
import re,json
s=Path('work/fresh-20260913/runtime.log').read_text();loaded={int(x) for x in re.findall(r'explorer: P(\d+);',s)}
scenes=json.loads(Path('outputs/astronomica-cleanroom/scene-index.json').read_text())
for row in scenes:
 id=int(row['place'][1:])
 if id not in loaded:print(row)
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp');s=p.read_text().replace('if (!file.open(Common::FSNode(path)) || file.size() < 4)', 'if (!Common::FSNode(path).exists() || !file.open(Common::FSNode(path)) || file.size() < 4)').replace('  _screen.free();\n  return loaded', '  _screen.free();\n  quitGame();\n  return loaded');p.write_text(s);Path('work/fresh-20260913/scummvm/engines/astronomica/astronomica.cpp').write_text(s)
