from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica/script.cpp');s=p.read_text();a=s.index('   // The original sets a scene-change request');b=s.index('   break;',a);s=s[:a]+s[b:];needle=''' return true;
}
bool ScriptRunner::start''';assert needle in s
s=s.replace(needle,''' // Follow only continuations that can execute before the scene reload.
 // Delayed (including zero-delay) work is queued and discarded on reload.
 Common::Array<int> links; links.resize(script.size());
 int condition = -1;
 for (uint i = 0; i < script.size(); ++i) {
  links[i] = -1;
  if (script[i].opcode == 31) condition = i;
  if (condition >= 0 && i+1 < script.size()) {
   if (script[i].opcode == 45) links[condition] = i;
   if (script[i].opcode == 42) links[condition] = i+1;
  }
 }
 for (uint root = 0; root < script.size(); ++root) if (script[root].opcode == 5) {
  Common::Array<int> work; work.push_back(root+1);
  Common::Array<bool> seen; seen.resize(script.size());
  for (uint i = 0; i < seen.size(); ++i) seen[i] = false;
  for (uint w = 0; w < work.size(); ++w) {
   const int index = work[w];
   if (index < 0 || uint(index) >= script.size() || seen[index] || script[index].delay != -1) continue;
   seen[index] = true;
   const int opcode = script[index].opcode;
   if (opcode != 1 && opcode != 2 && opcode != 31 && opcode != 42 && opcode != 45) return false;
   work.push_back(index+1);
   if (opcode == 31) work.push_back(links[index]);
   if (opcode == 45 && uint(index+1) < script.size()) work.push_back(links[index+1]);
  }
 }
 return true;
}
bool ScriptRunner::start''');p.write_text(s)
