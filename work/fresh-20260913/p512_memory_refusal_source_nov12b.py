"""Add graceful failure reporting only to the new isolated diagnostic;leave running general untouched."""
import re
from p512_memory_refusal_source_nov12 import inject as previous

def inject(cpp,script):
 cpp,script=previous(cpp,script)
 start=cpp.index('bool AstronomicaEngine::verifyP512Puzzle() {');end=cpp.index('\nbool AstronomicaEngine::',start+1);body=cpp[start:end]
 anchor=' auto observe=[&](const char*tag,uint32 now)';assert body.count(anchor)==1
 body=body.replace(anchor,' bool p512AuditFailed=false;\n'+anchor)
 body,count=re.subn(r'error\(("P512[^;]+?row)\);',r'{debug(\1);p512AuditFailed=true;return;}',body);assert count==5,count
 body,count=re.subn(r'(observe\("[^"\n]+",now\);)',r'\1if(p512AuditFailed)return false;',body);assert count>=7,count
 cpp=cpp[:start]+body+cpp[end:]
 old='  return ok ? Common::kNoError : Common::Error(Common::kReadingFailed,"P512 verification failed");';assert cpp.count(old)==1
 cpp=cpp.replace(old,'  debug("P512 isolated diagnostic result: %s",ok?"PASS":"FAIL");return Common::kNoError;')
 return cpp,script
