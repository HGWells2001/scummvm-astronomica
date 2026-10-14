from pathlib import Path
import shutil
r=Path('outputs/astronomica-cleanroom/engine/astronomica')
p=r/'script.h';s=p.read_text().replace('memset(_known, 0, sizeof(_known));', 'memset(_widths, 0, sizeof(_widths)); memset(_known, 0, sizeof(_known));').replace(' int32 _values[2][100];', ' int32 _values[2][100];\n int32 _widths[2][100];');p.write_text(s)
p=r/'script.cpp';s=p.read_text().replace(' memset(_known[1], 0, sizeof(_known[1]));', ' memset(_known[1], 0, sizeof(_known[1]));\n memset(_widths[1], 0, sizeof(_widths[1]));')
s=s.replace(' for (uint i = 0; i < conditions.size(); ++i)\n  if (conditions[i].raw[0] == 1)\n   defineValue(1, conditions[i].raw[1], conditions[i].raw[3]);', ''' for (uint i = 0; i < conditions.size(); ++i) {
  const Condition &c = conditions[i];
  if (c.raw[0] >= 0 && c.raw[0] <= 1 && c.raw[1] >= 0 && c.raw[1] < 100)
   _widths[c.raw[0]][c.raw[1]] = c.raw[2];
  if (c.raw[0] == 1) defineValue(1, c.raw[1], c.raw[3]);
 }''')
s=s.replace('  if (c.opcode == 9 &&', '''  if (c.opcode == 39) {
   int32 v;
   if (!getValue(c.args[0],c.args[1],v) || !getValue(c.args[2],c.args[3],v) || _widths[c.args[0]][c.args[1]] < 1 || _widths[c.args[0]][c.args[1]] > 31) return false;
  }
  if (c.opcode == 9 &&''',1)
s=s.replace('  case 40:', '''  case 39:
   if (c.args.size() != 4 || c.args[0] < 0 || c.args[0] > 1 || c.args[2] < 0 || c.args[2] > 1 || c.args[1] < 0 || c.args[1] >= 100 || c.args[3] < 0 || c.args[3] >= 100) return false;
   break;
  case 40:''',1)
s=s.replace('  } else if (c.opcode == 40) {', '''  } else if (c.opcode == 39) {
   const uint32 original = uint32(_values[c.args[0]][c.args[1]]);
   const int width = _widths[c.args[0]][c.args[1]];
   uint available = 0;
   for (int bit = 0; bit < width; ++bit) if (!(original & (uint32(1) << bit))) ++available;
   // _RangedRdm(1,0) still consumes a draw when the mask is exhausted.
   const uint selected = 1 + uint32(random15()) * available / 32768;
   uint rank = 0;
   for (int bit = 0; bit < width; ++bit) {
    if (!(original & (uint32(1) << bit))) ++rank;
    if (rank == selected) {
     _values[c.args[0]][c.args[1]] = int32(uint32(_values[c.args[0]][c.args[1]]) | (uint32(1) << bit));
     _values[c.args[2]][c.args[3]] = bit + 1;
     break;
    }
   }
  } else if (c.opcode == 40) {''');p.write_text(s)
p=r/'astronomica.cpp';s=p.read_text();anchor='  // Full, unmodified P29 entry program:'
test='''  bool bagOK = loadPlace(505);
  Script bagCommand;
  for (uint j = 0; j < _scene.scripts.size(); ++j)
   for (uint i = 0; i < _scene.scripts[j].size(); ++i)
    if (_scene.scripts[j][i].opcode == 39) bagCommand.push_back(_scene.scripts[j][i]);
  bagOK = bagCommand.size() == 1 && bagOK;
  _runner.seedRandom(1);
  uint seenVariants = 0;
  for (uint i = 0; i < 8; ++i) {
   bagOK = _runner.enqueue(bagCommand,0) && bagOK;
   runScriptsAt(0);
   int32 variant = 0, used = 0;
   bagOK = _runner.getValue(1,0,variant) && _runner.getValue(1,1,used) && variant >= 1 && variant <= 8 && bagOK;
   if (variant >= 1 && variant <= 8) {
    bagOK = !(seenVariants & (1U << (variant-1))) && bagOK;
    seenVariants |= 1U << (variant-1);
   }
   bagOK = uint32(used) == seenVariants && bagOK;
  }
  int32 lastVariant = 0, afterExhaustion = 0;
  _runner.getValue(1,0,lastVariant);
  bagOK = _runner.enqueue(bagCommand,0) && bagOK; runScriptsAt(0);
  bagOK = seenVariants == 255 && _runner.getValue(1,0,afterExhaustion) && afterExhaustion == lastVariant && _runner.random15() == 31126 && bagOK;
  debug("Astronomica variant bag verification: %s (original P505, eight distinct variants, exhausted mask preserves result and consumes draw)", bagOK ? "PASS" : "FAIL");
  scriptsOK = bagOK && scriptsOK;
'''
s=s.replace(anchor,test+anchor);p.write_text(s)
for p in r.iterdir(): shutil.copy2(p,Path('work/fresh-20260913/scummvm/engines/astronomica')/p.name)
