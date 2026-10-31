#include "astronomica/sprites.h"
// SPDX-License-Identifier: GPL-3.0-or-later
#include "astronomica/script.h"
#include "common/debug.h"
#include <initializer_list>
#include "astronomica/mentors.h"
#include "astronomica/advice.h"
namespace Astronomica {
int ScriptRunner::photonAnswer(int setting, int scenario) {
 // custom10/1, including the ineffective setting3/scenario11 branch.
 static const int required[] = {7,2,2,2,8,1,8,7,6,2,5,9,4,5};
 if (scenario < 1 || scenario > 14) return 11;
 const int target = required[scenario-1];
 return setting == target ? -1 : setting < target ? 10 : 11;
}
int ScriptRunner::weatherAnswer(int scenario, int a, int b, int c) {
 // Original custom24/0, 4:52bc-5632. Return the first error's direct
 // sound ID, -1 for acceptance, -2 when the original switch does nothing.
 static const int required[6][3] = {{8,8,15},{15,8,8},{15,8,8},{15,8,8},{8,15,8},{8,15,15}};
 if (scenario < 1 || scenario > 6) return -2;
 const int values[] = {a,b,c};
 for (int i = 0; i < 3; ++i)
  if (required[scenario-1][i] == 15 ? values[i] != 15 : values[i] > 8) return 12-i;
 return -1;
}
int ScriptRunner::successGlobalForPlace(int place) {
 switch (place) {
 case 501: return 20;
 case 504: return 21;
 case 505: return 22;
 case 506: return 23;
 case 508: return 24;
 case 509: return 25;
 case 510: return 26;
 case 511: return 27;
 case 512: return 28;
 case 513: return 29;
 case 514: return 30;
 case 516: return 32;
 case 517: return 33;
 case 518: return 34;
 case 519: return 35;
 case 520: return 36;
 case 521: return 37;
 case 522: return 38;
 case 523: return 39;
 case 524: return 40;
 case 525: return 41;
 case 526: return 42;
 case 527: return 43;
 case 528: return 44;
 case 529: return 45;
 case 530: return 46;
 case 531: return 23;
 case 532: return 23;
 case 533: return 23;
 case 534: return 23;
 case 535: return 23;
 case 536: return 31;
 default: return -1;
 }
}

uint16 ScriptRunner::random15() {
 // ASTRO.EXE 1:0b6b, including the 32-bit multiply helper at 1:0b3c.
 _randomState = _randomState * 0x015a4e35U + 1;
 return uint16((_randomState >> 16) & 0x7fff);
}
bool ScriptRunner::exportIdleState(Common::Array<uint32> &words) const {
 if (!idle()) return false;
 exportSettledValues(words); return true;
}
static bool sameP509Script(const Script&a,const Script&b){if(a.size()!=b.size())return false;for(uint i=0;i<a.size();++i)if(a[i].opcode!=b[i].opcode||a[i].delay!=b[i].delay||a[i].args!=b[i].args||a[i].text!=b[i].text)return false;return true;}
bool ScriptRunner::trustedP509Program()const{
 if(!_p509PendingSupport||_programs.size()!=6||_programs[5].size()!=25)return false;
 Script expected;auto add=[&](int opcode,int delay,std::initializer_list<int32>args){Command c;c.opcode=opcode;c.delay=delay;for(int32 v:args)c.args.push_back(v);expected.push_back(c);};
 add(31,0,{1,15,0,0,0,0});
 add(32,50,{1,14,1});
 add(45,-1,{});
 add(31,800,{1,3,1,0,0,0});
 add(9,0,{10});
 add(42,-1,{});
 add(31,0,{1,15,0,0,0,0});
 add(32,50,{1,14,1});
 add(45,-1,{});
 add(31,800,{1,4,1,0,0,0});
 add(9,0,{9});
 add(42,-1,{});
 add(31,0,{1,15,0,0,0,0});
 add(32,50,{1,14,1});
 add(45,-1,{});
 add(31,800,{1,5,1,0,0,0});
 add(9,0,{8});
 add(42,-1,{});
 add(31,0,{1,15,0,0,0,0});
 add(32,50,{1,14,1});
 add(45,-1,{});
 add(31,800,{1,1,1,0,0,0});
 add(9,0,{11});
 add(42,-1,{});
 add(41,800,{5});

 return sameP509Script(_programs[5],expected);
}
bool ScriptRunner::validP509PendingValues(const Common::Array<uint32>&w,uint32 now)const{
 if(w.size()!=608)return false;Common::Array<uint32>state;for(uint i=0;i<605;++i)state.push_back(w[i]);
 if(!validPersistentState(state)||w[605]!=5||w[606]!=3||int32(now-w[607])<0||int32(now-w[601])<0)return false;
 const uint widths[]={6,1,1,1,1,1,1,6,1,1,1,1,1,6,1,1,3};
 for(uint i=0;i<100;++i)if(w[3*i+2]!=1||(w[3*i+1]&&(i>=3||w[3*i+1]!=6))||w[302+3*i]!=uint32(i<17)||w[301+3*i]!=(i<17?widths[i]:0U))return false;
 if(w[300]||w[321]>6||w[339]>2||w[342]!=1||w[345]!=1||(w[348]!=1&&w[348]!=2))return false;
 for(uint i=1;i<=6;++i)if(w[300+3*i]>1)return false;for(uint i=8;i<=12;++i)if(w[300+3*i])return false;
 return true;
}
bool ScriptRunner::exportP509PendingState(Common::Array<uint32>&words,uint32 now)const{
 if(!trustedP509Program()||_pending.size()!=1||!_actions.empty()||_clicksBlocked)return false;const Pending&p=_pending[0];
 if(p.index!=3||!sameP509Script(p.script,_programs[5]))return false;Common::Array<uint32>w;exportSettledValues(w);w.push_back(_variantRound);w.push_back(_variantMask);w.push_back(5);w.push_back(3);w.push_back(p.since);
 if(!validP509PendingValues(w,now))return false;words=w;return true;
}
bool ScriptRunner::importP509PendingState(const Common::Array<uint32>&words,uint32 now){
 if(!trustedP509Program()||!scriptsIdle()||!validP509PendingValues(words,now))return false;
 for(uint i=0;i<100;++i)if(words[301+3*i]!=uint32(_widths[1][i])||words[302+3*i]!=uint32(_known[1][i]))return false;
 // All checks precede mutation. The live recipient retains original bindings.
 importSettledValues(words);_variantRound=words[603];_variantMask=words[604];_pending.push_back(Pending{_programs[5],3,words[607]});++_pendingEpoch;return true;
}
bool ScriptRunner::verifyP509PendingSnapshots(const ScriptRunner&recipient,uint32 observedNow)const{
 Common::Array<uint32>saved;if(!exportP509PendingState(saved,observedNow)||!recipient.scriptsIdle()||!recipient.trustedP509Program())return false;uint cases=0,rejected=0,originChecks=0;
 for(uint32 epoch:{saved[607],0xfffffff0U})for(uint32 age:{0U,1U,799U,800U,801U,1600U}){
  Common::Array<uint32>w=saved;const uint32 delta=epoch-saved[607];w[601]+=delta;w[607]=epoch;const uint32 now=epoch+age;
  ScriptRunner expected=*this,actual=recipient;expected.importSettledValues(w);expected._programLoadedAt=w[601];expected._pending[0].since=epoch;
  if(!actual.importP509PendingState(w,now))return false;Common::Array<uint32>again;if(!actual.exportP509PendingState(again,now)||again!=w)return false;
  // Diagnostic equality includes every605word, queued original command/index/
  // since, actions and click lock. No queue is cleared to create eligibility.
  auto equal=[&](){return expected.probeDiagnosticHash(false)==actual.probeDiagnosticHash(false);};
  if(!equal())return false;expected.tick(now);actual.tick(now);if(!equal()||actual._pending.size()!=1||actual._pending[0].index!=(age>=800?4U:3U))return false;
  for(uint32 at:{now,now+799,now+800,now+800,now+801,now+1600}){expected.tick(at);actual.tick(at);if(!equal())return false;}
  bool seen=false;for(uint n=0;n<10000;++n){const uint32 at=now+1601+n;expected.tick(at);actual.tick(at);if(!equal())return false;if(actual._pending.size()==1&&actual._pending[0].index==0){if(actual._pending[0].since!=w[601])return false;expected.tick(at);actual.tick(at);if(!equal()||actual._pending[0].index!=3||actual._pending[0].since!=at)return false;seen=true;break;}}
  if(!seen)return false;++originChecks;++cases;
 }
 auto reject=[&](const Common::Array<uint32>&bad,ScriptRunner target){const uint32 before=target.probeDiagnosticHash(true);if(target.importP509PendingState(bad,observedNow)||before!=target.probeDiagnosticHash(true))return false;++rejected;return true;};
 for(uint i:{2U,301U,302U,321U,339U,342U,345U,348U,602U,603U,604U,605U,606U,607U}){Common::Array<uint32>bad=saved;bad[i]=i==607?observedNow+1:0xffffffffU;if(!reject(bad,recipient))return false;}
 Common::Array<uint32>shortState=saved;shortState.resize(607);if(!reject(shortState,recipient))return false;
 for(uint kind=0;kind<6;++kind){ScriptRunner bad=recipient;if(kind==0)bad._programs[5][3].delay=801;if(kind==1)bad._pending.push_back(_pending[0]);if(kind==2)bad._actions.push_back(Action{});if(kind==3)bad._clicksBlocked=true;if(kind==4)bad._p509PendingSupport=false;if(kind==5)bad._known[1][0]=false;if(!reject(saved,bad))return false;}
 for(uint kind=0;kind<7;++kind){ScriptRunner bad=*this;if(kind==0)bad._pending.push_back(_pending[0]);if(kind==1)bad._pending[0].index=0;if(kind==2)bad._pending[0].index=4;if(kind==3)bad._pending[0].index=24;if(kind==4)bad._pending[0].script[3].delay=801;if(kind==5)bad._actions.push_back(Action{});if(kind==6)bad._clicksBlocked=true;Common::Array<uint32>out;out.push_back(123456);const Common::Array<uint32>before=out;const uint32 fingerprint=bad.probeDiagnosticHash(true);if(bad.exportP509PendingState(out,observedNow)||out!=before||bad.probeDiagnosticHash(true)!=fingerprint)return false;++rejected;}
 debug("Astronomica P509 pending kernel: PASS (%u timing cases, %u origin/reschedule checks, %u atomic/shape rejections; configured live binding, no save support)",cases,originChecks,rejected);return true;
}

// Diagnostic observation only: never an admitted save/export API.
void ScriptRunner::auditP509Snapshot(Common::Array<uint32>&values,Common::Array<uint32>&queue)const{
 exportSettledValues(values);values.push_back(_variantRound);values.push_back(_variantMask);queue.clear();
 for(const Pending&p:_pending){uint program=0xffffffffU;
  for(uint i=0;i<_programs.size();++i){const Script&s=_programs[i];bool equal=s.size()==p.script.size();for(uint j=0;equal&&j<s.size();++j){const Command&a=s[j],&b=p.script[j];equal=a.opcode==b.opcode&&a.delay==b.delay&&a.args==b.args;}if(equal){program=i;break;}}
  queue.push_back(program);queue.push_back(p.index);queue.push_back(p.since);queue.push_back(p.script[p.index].opcode);queue.push_back(p.script[p.index].delay);
 }
}
bool ScriptRunner::trustedP504PollProgram()const{
 if(!_p504PollSupport||!_cometHandler||_programs.size()!=3||_programs[0].size()!=11)return false;
 const int ops[]={31,32,45,31,32,9,23,9,5,42,41},delays[]={0,0,-1,0,0,400,4400,6500,3500,-1,200},counts[]={6,3,0,6,3,1,6,1,1,0,1};
 const int32 args[11][6]={{1,8,1,0,0,0},{1,8,1},{},{1,7,1,0,0,0},{1,8,1},{3},{25,0,0,0,0,0},{15},{527},{},{0}};
 for(uint i=0;i<11;++i){const Command&c=_programs[0][i];if(c.opcode!=ops[i]||c.delay!=delays[i]||c.args.size()!=uint(counts[i])||!c.text.empty())return false;for(uint j=0;j<c.args.size();++j)if(c.args[j]!=args[i][j])return false;}
 return true;
}
bool ScriptRunner::validP504PollValues(const Common::Array<uint32>&w,uint32 now)const{
 if(w.size()!=607||int32(now-w[601])<0||int32(now-w[606])<0||(w[605]!=0&&w[605]!=10)||(w[605]==0&&w[606]!=w[601]))return false;
 Common::Array<uint32>base;for(uint i=0;i<605;++i)base.push_back(w[i]);if(!validPersistentState(base)||w[300]<1||w[300]>4||w[303]>15||w[306]<1||w[306]>4||w[321]||w[324])return false;
 uint mask=0;for(uint i=3;i<=6;++i){if(w[300+3*i]>1)return false;mask|=w[300+3*i]<<(i-3);}if(mask==15)return false;
 for(uint i=0;i<100;++i){const uint width=i==0?8U:i==8?1U:i<9?20U:0U;if(w[301+3*i]!=width||w[302+3*i]!=uint32(i<9)||w[301+3*i]!=uint32(_widths[1][i])||w[302+3*i]!=uint32(_known[1][i]))return false;}
 return true;
}
bool ScriptRunner::exportP504PollState(Common::Array<uint32>&w,uint32 now)const{
 if(!trustedP504PollProgram()||_pending.size()!=1||!_actions.empty()||_clicksBlocked)return false;
 const Pending&p=_pending[0];if((p.index!=0&&p.index!=10)||p.script.size()!=11)return false;
 for(uint i=0;i<11;++i){const Command&a=p.script[i],&b=_programs[0][i];if(a.opcode!=b.opcode||a.delay!=b.delay||a.args!=b.args||a.text!=b.text)return false;}
 Common::Array<uint32>saved;exportSettledValues(saved);saved.push_back(_variantRound);saved.push_back(_variantMask);saved.push_back(p.index);saved.push_back(p.since);if(!validP504PollValues(saved,now))return false;w=saved;return true;
}
bool ScriptRunner::importP504PollState(const Common::Array<uint32>&w,uint32 now){
 if(!trustedP504PollProgram()||!scriptsIdle()||!validP504PollValues(w,now))return false;
 importSettledValues(w);_variantRound=w[603];_variantMask=w[604];_pending.push_back(Pending{_programs[0],w[605],w[606]});++_pendingEpoch;return true;
}
bool ScriptRunner::verifyP504PollSnapshots()const{
 Common::Array<uint32>base;if(!exportP504PollState(base,0))return false;uint cases=0,rejected=0,excluded=0;
 for(uint index:{0U,10U})for(uint32 origin:{1000U,0xfffffff0U})for(uint age:{0U,1U,199U,200U,201U,1000U}){
  Common::Array<uint32>w=base;w[601]=origin;w[605]=index;w[606]=index?origin+200:origin;const uint32 now=w[606]+age;
  ScriptRunner expected=*this,actual=*this;expected.clear();actual.clear();expected.importSettledValues(w);expected._variantRound=w[603];expected._variantMask=w[604];expected._pending.push_back(Pending{expected._programs[0],index,w[606]});
  if(!actual.importP504PollState(w,now)||expected.probeDiagnosticHash(false)!=actual.probeDiagnosticHash(false))return false;
  for(uint n=0;n<101;++n){const uint32 at=now+n*10;expected.tick(at);actual.tick(at);if(expected.probeDiagnosticHash(false)!=actual.probeDiagnosticHash(false))return false;for(const Pending&p:actual._pending)if(p.index==0&&p.since!=origin)return false;}
  ++cases;
 }
 ScriptRunner recipient=*this;recipient.clear();const uint32 untouched=recipient.probeDiagnosticHash(true);
 auto reject=[&](const Common::Array<uint32>&w,uint32 now){if(recipient.importP504PollState(w,now)||recipient.probeDiagnosticHash(true)!=untouched)return false;++rejected;return true;};
 for(uint at:{300U,303U,306U,309U,321U,324U,301U,302U,601U,605U,606U}){Common::Array<uint32>w=base;w[at]=(at==601||at==606)?1U:0xfffffffeU;if(!reject(w,0)){debug("P504 poll invalid fixture failed at%u",at);return false;}}
 Common::Array<uint32>bad=base;bad[605]=3;if(!reject(bad,0))return false;bad=base;bad.remove_at(606);if(!reject(bad,0))return false;
 for(uint kind=0;kind<6;++kind){ScriptRunner badRunner=*this;if(kind==0)badRunner._pending[0].index=3;if(kind==1)badRunner._pending.push_back(badRunner._pending[0]);if(kind==2)badRunner._actions.push_back(Action{});if(kind==3)badRunner._clicksBlocked=true;if(kind==4)badRunner._programs[0][3].args[2]=0;if(kind==5)badRunner._p504PollSupport=false;Common::Array<uint32>out;out.push_back(123);const Common::Array<uint32>before=out;const uint32 old=badRunner.probeDiagnosticHash(true);if(badRunner.exportP504PollState(out,0)||out!=before||badRunner.probeDiagnosticHash(true)!=old)return false;++excluded;}
 debug("Astronomica P504 poll kernel snapshots: PASS (%u timing cases, %u atomic import rejections, %u rejected export shapes; index3 explicitly excluded)",cases,rejected,excluded);return cases==24&&rejected==13&&excluded==6;
}

bool ScriptRunner::trustedP501ReadyProgram()const{
 if(!_p501ReadySupport||!_ballHandler||_programs.size()!=1||_programs[0].size()!=8)return false;
 const int ops[]={31,28,10,23,5,29,42,41},delays[]={0,0,3500,0,3500,150,-1,200},counts[]={6,1,1,6,1,1,0,1};const int32 args[8][6]={{1,3,1,0,0,0},{-1},{-1},{25,0,0,0,0,0},{388},{-1},{},{0}};
 for(uint i=0;i<8;++i){const Command&c=_programs[0][i];if(c.opcode!=ops[i]||c.delay!=delays[i]||c.args.size()!=uint(counts[i])||!c.text.empty())return false;for(uint j=0;j<c.args.size();++j)if(c.args[j]!=args[i][j])return false;}return true;
}
bool ScriptRunner::validP501ReadyValues(const Common::Array<uint32>&w,uint32 now)const{
 if(w.size()!=607||int32(now-w[601])<0||int32(now-w[606])<0||(w[605]!=0&&w[605]!=7)||(w[605]==0&&w[606]!=w[601]))return false;
 Common::Array<uint32>base;for(uint i=0;i<605;++i)base.push_back(w[i]);if(!validPersistentState(base)||w[300]>5||w[303]||w[306]>2||w[309]||w[312]!=1)return false;
 for(uint i=0;i<100;++i)if(w[301+3*i]!=uint32(_widths[1][i])||w[302+3*i]!=uint32(_known[1][i]))return false;return true;
}
bool ScriptRunner::exportP501ReadyState(Common::Array<uint32>&w,uint32 now)const{
 if(!trustedP501ReadyProgram()||_pending.size()!=1||!_actions.empty()||_clicksBlocked)return false;const Pending&p=_pending[0];if((p.index!=0&&p.index!=7)||p.script.size()!=8)return false;
 for(uint i=0;i<8;++i){const Command&a=p.script[i],&b=_programs[0][i];if(a.opcode!=b.opcode||a.delay!=b.delay||a.args!=b.args||a.text!=b.text)return false;}
 Common::Array<uint32>saved;exportSettledValues(saved);saved.push_back(_variantRound);saved.push_back(_variantMask);saved.push_back(p.index);saved.push_back(p.since);if(!validP501ReadyValues(saved,now))return false;w=saved;return true;
}
bool ScriptRunner::importP501ReadyState(const Common::Array<uint32>&w,uint32 now){
 if(!trustedP501ReadyProgram()||!scriptsIdle()||!validP501ReadyValues(w,now))return false;importSettledValues(w);_variantRound=w[603];_variantMask=w[604];_pending.push_back(Pending{_programs[0],w[605],w[606]});++_pendingEpoch;return true;
}

void ScriptRunner::swapP510PreparedRunner(ScriptRunner&o){
 _programs.swap(o._programs);
 _pending.swap(o._pending);
 _actions.swap(o._actions);
 _spriteTargets.swap(o._spriteTargets);
 _soundTargets.swap(o._soundTargets);
 _movieDurations.swap(o._movieDurations);
 _imageTargets.swap(o._imageTargets);
 {auto value=_p501ReadySupport;_p501ReadySupport=o._p501ReadySupport;o._p501ReadySupport=value;}
 {auto value=_p504PollSupport;_p504PollSupport=o._p504PollSupport;o._p504PollSupport=value;}
 {auto value=_p509PendingSupport;_p509PendingSupport=o._p509PendingSupport;o._p509PendingSupport=value;}
 {auto value=_programLoadedAt;_programLoadedAt=o._programLoadedAt;o._programLoadedAt=value;}
 {auto value=_pendingEpoch;_pendingEpoch=o._pendingEpoch;o._pendingEpoch=value;}
 {auto value=_ballHandler;_ballHandler=o._ballHandler;o._ballHandler=value;}
 {auto value=_cometHandler;_cometHandler=o._cometHandler;o._cometHandler=value;}
 {auto value=_nativePaletteSupport;_nativePaletteSupport=o._nativePaletteSupport;o._nativePaletteSupport=value;}
 {auto value=_jupiterSupport;_jupiterSupport=o._jupiterSupport;o._jupiterSupport=value;}
 {auto value=_plotSupport;_plotSupport=o._plotSupport;o._plotSupport=value;}
 {auto value=_dangerSupport;_dangerSupport=o._dangerSupport;o._dangerSupport=value;}
 {auto value=_probeHandler;_probeHandler=o._probeHandler;o._probeHandler=value;}
 {auto value=_rendezvousHandler;_rendezvousHandler=o._rendezvousHandler;o._rendezvousHandler=value;}
 {auto value=_lastTrue;_lastTrue=o._lastTrue;o._lastTrue=value;}
 {auto value=_clicksBlocked;_clicksBlocked=o._clicksBlocked;o._clicksBlocked=value;}
 {auto value=_executed;_executed=o._executed;o._executed=value;}
 {auto value=_randomState;_randomState=o._randomState;o._randomState=value;}
 {auto value=_gameStateHandler;_gameStateHandler=o._gameStateHandler;o._gameStateHandler=value;}
 {auto value=_soundHandler;_soundHandler=o._soundHandler;o._soundHandler=value;}
 {auto value=_orbitHandler;_orbitHandler=o._orbitHandler;o._orbitHandler=value;}
 {auto value=_successHandler;_successHandler=o._successHandler;o._successHandler=value;}
 {auto value=_successGlobal;_successGlobal=o._successGlobal;o._successGlobal=value;}
 {auto value=_successExtraGlobal;_successExtraGlobal=o._successExtraGlobal;o._successExtraGlobal=value;}
 {auto value=_rocketSupport;_rocketSupport=o._rocketSupport;o._rocketSupport=value;}
 {auto value=_eclipseSupport;_eclipseSupport=o._eclipseSupport;o._eclipseSupport=value;}
 {auto value=_planetSupport;_planetSupport=o._planetSupport;o._planetSupport=value;}
 {auto value=_variantSupport;_variantSupport=o._variantSupport;o._variantSupport=value;}
 {auto value=_weatherSupport;_weatherSupport=o._weatherSupport;o._weatherSupport=value;}
 {auto value=_mentorSupport;_mentorSupport=o._mentorSupport;o._mentorSupport=value;}
 {auto value=_adviceSupport;_adviceSupport=o._adviceSupport;o._adviceSupport=value;}
 {auto value=_mentorPrevious;_mentorPrevious=o._mentorPrevious;o._mentorPrevious=value;}
 {auto value=_worldMovieSupport;_worldMovieSupport=o._worldMovieSupport;o._worldMovieSupport=value;}
 {auto value=_helpSupport;_helpSupport=o._helpSupport;o._helpSupport=value;}
 {auto value=_legacyResumeSupport;_legacyResumeSupport=o._legacyResumeSupport;o._legacyResumeSupport=value;}
 {auto value=_resumeSupport;_resumeSupport=o._resumeSupport;o._resumeSupport=value;}
 {auto value=_resumeFromHelp;_resumeFromHelp=o._resumeFromHelp;o._resumeFromHelp=value;}
 {auto value=_photonSupport;_photonSupport=o._photonSupport;o._photonSupport=value;}
 {auto value=_zodiacSupport;_zodiacSupport=o._zodiacSupport;o._zodiacSupport=value;}
 {auto value=_zodiacRegion;_zodiacRegion=o._zodiacRegion;o._zodiacRegion=value;}
 {auto value=_noopSuccess;_noopSuccess=o._noopSuccess;o._noopSuccess=value;}
 {auto value=_variantRound;_variantRound=o._variantRound;o._variantRound=value;}
 {auto value=_variantMask;_variantMask=o._variantMask;o._variantMask=value;}
 for(uint scope=0;scope<2;++scope)for(uint i=0;i<100;++i){int32 value=_values[scope][i];_values[scope][i]=o._values[scope][i];o._values[scope][i]=value;value=_widths[scope][i];_widths[scope][i]=o._widths[scope][i];o._widths[scope][i]=value;bool known=_known[scope][i];_known[scope][i]=o._known[scope][i];o._known[scope][i]=known;}
}

uint32 ScriptRunner::p510CompleteHash()const{
 uint32 h=probeDiagnosticHash(true);auto add=[&](uint32 v){h=(h^v)*16777619U;};
 add(uint32(_p501ReadySupport));
 add(uint32(_p504PollSupport));
 add(uint32(_p509PendingSupport));
 add(uint32(_programLoadedAt));
 add(uint32(_pendingEpoch));
 {uint64 ptr=uint64(reinterpret_cast<uintptr_t>(_ballHandler));add(uint32(ptr));add(uint32(ptr>>32));}
 {uint64 ptr=uint64(reinterpret_cast<uintptr_t>(_cometHandler));add(uint32(ptr));add(uint32(ptr>>32));}
 add(uint32(_nativePaletteSupport));
 add(uint32(_jupiterSupport));
 add(uint32(_plotSupport));
 add(uint32(_dangerSupport));
 {uint64 ptr=uint64(reinterpret_cast<uintptr_t>(_probeHandler));add(uint32(ptr));add(uint32(ptr>>32));}
 {uint64 ptr=uint64(reinterpret_cast<uintptr_t>(_rendezvousHandler));add(uint32(ptr));add(uint32(ptr>>32));}
 add(uint32(_lastTrue));
 add(uint32(_clicksBlocked));
 add(uint32(_executed));
 add(uint32(_randomState));
 {uint64 ptr=uint64(reinterpret_cast<uintptr_t>(_gameStateHandler));add(uint32(ptr));add(uint32(ptr>>32));}
 {uint64 ptr=uint64(reinterpret_cast<uintptr_t>(_soundHandler));add(uint32(ptr));add(uint32(ptr>>32));}
 {uint64 ptr=uint64(reinterpret_cast<uintptr_t>(_orbitHandler));add(uint32(ptr));add(uint32(ptr>>32));}
 {uint64 ptr=uint64(reinterpret_cast<uintptr_t>(_successHandler));add(uint32(ptr));add(uint32(ptr>>32));}
 add(uint32(_successGlobal));
 add(uint32(_successExtraGlobal));
 add(uint32(_rocketSupport));
 add(uint32(_eclipseSupport));
 add(uint32(_planetSupport));
 add(uint32(_variantSupport));
 add(uint32(_weatherSupport));
 add(uint32(_mentorSupport));
 add(uint32(_adviceSupport));
 add(uint32(_mentorPrevious));
 add(uint32(_worldMovieSupport));
 add(uint32(_helpSupport));
 add(uint32(_legacyResumeSupport));
 add(uint32(_resumeSupport));
 add(uint32(_resumeFromHelp));
 add(uint32(_photonSupport));
 add(uint32(_zodiacSupport));
 add(uint32(_zodiacRegion));
 add(uint32(_noopSuccess));
 add(uint32(_variantRound));
 add(uint32(_variantMask));

 for(uint32 value:_movieDurations)add(value);for(const Common::String&name:_imageTargets)for(char c:name)add(byte(c));
 for(const Script&program:_programs){add(program.size());for(const Command&c:program){add(c.opcode);add(c.delay);for(int32 v:c.args)add(uint32(v));for(char v:c.text)add(byte(v));}}return h;
}
bool ScriptRunner::p510Capabilities(GameStateHandler*g,SoundHandler*s,SuccessHandler*success,const Scene&scene)const{
 if(!_plotSupport||_gameStateHandler!=g||_soundHandler!=s||_successHandler!=success||_successGlobal!=26||_successExtraGlobal!=-1||_spriteTargets.size()!=14||_soundTargets.size()!=923||!_soundTargets[912]||_movieDurations.size()!=1||_movieDurations[0]!=11340||!_imageTargets.empty())return false;
 if(_p501ReadySupport||_p504PollSupport||_p509PendingSupport||_ballHandler||_cometHandler||_nativePaletteSupport||_jupiterSupport||_dangerSupport||_probeHandler||_rendezvousHandler||_orbitHandler||_rocketSupport||_eclipseSupport||_planetSupport||_variantSupport||_weatherSupport||_mentorSupport||_adviceSupport||_worldMovieSupport||_helpSupport||_legacyResumeSupport||_resumeSupport||_resumeFromHelp||_photonSupport||_zodiacSupport||_noopSuccess)return false;
 for(uint i=0;i<14;++i)if(_spriteTargets[i]!=spriteFrameCount(scene,i))return false;return true;
}

bool ScriptRunner::trustedP510ActiveProgram()const{
if(!_plotSupport||_programs.size()!=4)return false;
if(_programs[0].size()!=13)return false;
{const Command&c=_programs[0][0];if(c.opcode!=4||c.delay!=0||c.args.size()!=1||!c.text.empty())return false;
if(c.args[0]!=0)return false;
}
{const Command&c=_programs[0][1];if(c.opcode!=36||c.delay!=0||c.args.size()!=2||!c.text.empty())return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=0)return false;
}
{const Command&c=_programs[0][2];if(c.opcode!=40||c.delay!=0||c.args.size()!=4||!c.text.empty())return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=1)return false;
if(c.args[3]!=3)return false;
}
{const Command&c=_programs[0][3];if(c.opcode!=31||c.delay!=0||c.args.size()!=6||!c.text.empty())return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=1)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[0][4];if(c.opcode!=23||c.delay!=0||c.args.size()!=6||!c.text.empty())return false;
if(c.args[0]!=23)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=0)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[0][5];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;
}
{const Command&c=_programs[0][6];if(c.opcode!=31||c.delay!=0||c.args.size()!=6||!c.text.empty())return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=2)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[0][7];if(c.opcode!=23||c.delay!=0||c.args.size()!=6||!c.text.empty())return false;
if(c.args[0]!=23)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=0)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[0][8];if(c.opcode!=45||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;
}
{const Command&c=_programs[0][9];if(c.opcode!=31||c.delay!=0||c.args.size()!=6||!c.text.empty())return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=3)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[0][10];if(c.opcode!=23||c.delay!=0||c.args.size()!=6||!c.text.empty())return false;
if(c.args[0]!=23)return false;
if(c.args[1]!=3)return false;
if(c.args[2]!=0)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[0][11];if(c.opcode!=42||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;
}
{const Command&c=_programs[0][12];if(c.opcode!=3||c.delay!=0||c.args.size()!=4||!c.text.empty())return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=261)return false;
if(c.args[2]!=33)return false;
if(c.args[3]!=0)return false;
}
if(_programs[1].size()!=7)return false;
{const Command&c=_programs[1][0];if(c.opcode!=46||c.delay!=0||c.args.size()!=3||!c.text.empty())return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=-1)return false;
}
{const Command&c=_programs[1][1];if(c.opcode!=47||c.delay!=0||c.args.size()!=3||!c.text.empty())return false;
if(c.args[0]!=8)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=1)return false;
}
{const Command&c=_programs[1][2];if(c.opcode!=47||c.delay!=0||c.args.size()!=3||!c.text.empty())return false;
if(c.args[0]!=9)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=1)return false;
}
{const Command&c=_programs[1][3];if(c.opcode!=31||c.delay!=0||c.args.size()!=6||!c.text.empty())return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=0)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[1][4];if(c.opcode!=5||c.delay!=0||c.args.size()!=1||!c.text.empty())return false;
if(c.args[0]!=136)return false;
}
{const Command&c=_programs[1][5];if(c.opcode!=42||c.delay!=-1||c.args.size()!=0||!c.text.empty())return false;
}
{const Command&c=_programs[1][6];if(c.opcode!=41||c.delay!=2750||c.args.size()!=1||!c.text.empty())return false;
if(c.args[0]!=1)return false;
}
if(_programs[2].size()!=1)return false;
{const Command&c=_programs[2][0];if(c.opcode!=15||c.delay!=0||c.args.size()!=2||!c.text.empty())return false;
if(c.args[0]!=12)return false;
if(c.args[1]!=1)return false;
}
if(_programs[3].size()!=1)return false;
{const Command&c=_programs[3][0];if(c.opcode!=25||c.delay!=0||c.args.size()!=0||!c.text.empty())return false;
}
return true;
}

bool ScriptRunner::validP510ActiveValues(const Common::Array<uint32>&w,uint32 now)const{
 if(w.size()!=607||w[605]!=6||int32(now-w[601])<0||int32(now-w[606])<0)return false;
 Common::Array<uint32>base;for(uint i=0;i<605;++i)base.push_back(w[i]);if(!validPersistentState(base))return false;
 const uint widths[]={12,52,3,16,8,1,3};for(uint i=0;i<100;++i)if(w[301+3*i]!=(i<7?widths[i]:0U)||w[302+3*i]!=uint32(i<7))return false;
 return w[300]>=1&&w[300]<=3&&w[303]>=1&&w[303]<=51&&!w[306]&&!w[309]&&w[312]>=1&&w[312]<=5&&w[315]==1&&!w[318];
}
bool ScriptRunner::exportP510ActiveState(Common::Array<uint32>&words,uint32 now)const{
 if(!trustedP510ActiveProgram()||_pending.size()!=1||!_actions.empty()||_clicksBlocked)return false;const Pending&p=_pending[0];if(p.index!=6||p.script.size()!=_programs[1].size())return false;
 for(uint i=0;i<p.script.size();++i){const Command&a=p.script[i],&b=_programs[1][i];if(a.opcode!=b.opcode||a.delay!=b.delay||a.args!=b.args||a.text!=b.text)return false;}
 Common::Array<uint32>w;exportSettledValues(w);w.push_back(_variantRound);w.push_back(_variantMask);w.push_back(p.index);w.push_back(p.since);if(!validP510ActiveValues(w,now))return false;words=w;return true;
}
bool ScriptRunner::importP510ActiveState(const Common::Array<uint32>&words,uint32 now){
 if(!trustedP510ActiveProgram()||!scriptsIdle()||_clicksBlocked||!validP510ActiveValues(words,now))return false;
 importSettledValues(words);_variantRound=words[603];_variantMask=words[604];_pending.push_back(Pending{_programs[1],words[605],words[606]});++_pendingEpoch;return true;
}
bool ScriptRunner::testP510ActiveState(uint32 now)const{
 Common::Array<uint32>w;if(!exportP510ActiveState(w,now))return false;ScriptRunner prepared;prepared.setPrograms(_programs,w[601]);prepared.setPlotSupport(true);
 if(!prepared.importP510ActiveState(w,now)||prepared.probeDiagnosticHash(false)!=probeDiagnosticHash(false))return false;
 Common::Array<uint32>again;if(!prepared.exportP510ActiveState(again,now)||again!=w)return false;
 ScriptRunner expected=*this;for(uint32 at:{now,now+2749,now+2750,now+2751}){expected.tick(at);prepared.tick(at);if(expected.probeDiagnosticHash(false)!=prepared.probeDiagnosticHash(false))return false;}

 {Common::Array<uint32>bad=w;bad[303]=52;ScriptRunner target;target.setPrograms(_programs,w[601]);target.setPlotSupport(true);const uint32 before=target.probeDiagnosticHash(true);if(target.importP510ActiveState(bad,now)||target.probeDiagnosticHash(true)!=before)return false;debug("P510 countdown52 phase rejection: PASS (literal width52 unchanged)");}
 for(uint offset:{300U,303U,304U,306U,309U,312U,313U,315U,318U,602U,605U,606U}){Common::Array<uint32>bad=w;bad[offset]=offset==606?now+1:0xffffffffU;ScriptRunner target;target.setPrograms(_programs,w[601]);target.setPlotSupport(true);const uint32 before=target.probeDiagnosticHash(true);if(target.importP510ActiveState(bad,now)||target.probeDiagnosticHash(true)!=before){debug("P510 runner invalid fixture FAIL offset%u",offset);return false;}}
 return true;
}
void ScriptRunner::p510AuditExportState(Common::Array<uint32>&words)const{exportSettledValues(words);words.push_back(_variantRound);words.push_back(_variantMask);}
void ScriptRunner::p510AuditPending(const char*tag,uint32 now)const{
 debug("P510QUEUE %s now=%u loaded=%u pending=%u actions=%u blocked=%u",tag,now,_programLoadedAt,_pending.size(),_actions.size(),uint(_clicksBlocked));
 for(uint i=0;i<_pending.size();++i){const Pending&p=_pending[i];int program=-1;for(uint j=0;j<_programs.size();++j)if(p.script.size()==_programs[j].size()){bool same=true;for(uint k=0;k<p.script.size();++k){const Command&a=p.script[k],&b=_programs[j][k];same&=a.opcode==b.opcode&&a.delay==b.delay&&a.args==b.args&&a.text==b.text;}if(same)program=j;}debug("P510PENDING %s now=%u program=%d index=%u since=%u count=%u",tag,now,program,p.index,p.since,p.script.size());}
}
bool ScriptRunner::p512Capabilities(GameStateHandler*g,SoundHandler*s,SuccessHandler*success,const Scene&scene)const{
 if(!trustedP512SettledProgram()||!_weatherSupport||_gameStateHandler!=g||_soundHandler!=s||_successHandler!=success||_successGlobal!=28||_successExtraGlobal!=-1||_spriteTargets.size()!=64||_soundTargets.size()!=923||!_soundTargets[912]||!_soundTargets[302]||_movieDurations.size()!=1||_movieDurations[0]!=1928||_imageTargets.size()!=6)return false;
 if(_p501ReadySupport||_p504PollSupport||_p509PendingSupport||_ballHandler||_cometHandler||_nativePaletteSupport||_jupiterSupport||_plotSupport||_dangerSupport||_probeHandler||_rendezvousHandler||_orbitHandler||_rocketSupport||_eclipseSupport||_planetSupport||_variantSupport||_mentorSupport||_adviceSupport||_worldMovieSupport||_helpSupport||_legacyResumeSupport||_resumeSupport||_resumeFromHelp||_photonSupport||_zodiacSupport||_noopSuccess)return false;
 for(uint i=0;i<64;++i)if(_spriteTargets[i]!=spriteFrameCount(scene,i))return false;for(uint i=0;i<=14;++i)if(!_soundTargets[i])return false;
 const char*names[]={"MOONCOR","MOONHALO","SUNDOGS","SUNHALO","SUNPILL","CREPRAYS"};for(uint i=0;i<6;++i)if(_imageTargets[i]!=names[i])return false;return true;
}
bool ScriptRunner::trustedP512SettledProgram()const{
if(!_weatherSupport||_programs.size()!=6)return false;
if(_programs[0].size()!=1)return false;
{const Command&c=_programs[0][0];if(c.opcode!=39||c.delay!=0||c.offset!=367810||c.args.size()!=4||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=3)return false;
if(c.args[2]!=1)return false;
if(c.args[3]!=4)return false;
}
if(_programs[1].size()!=8)return false;
{const Command&c=_programs[1][0];if(c.opcode!=17||c.delay!=0||c.offset!=367838||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=15)return false;
}
{const Command&c=_programs[1][1];if(c.opcode!=17||c.delay!=-1||c.offset!=367850||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=16)return false;
}
{const Command&c=_programs[1][2];if(c.opcode!=17||c.delay!=-1||c.offset!=367862||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=17)return false;
}
{const Command&c=_programs[1][3];if(c.opcode!=17||c.delay!=-1||c.offset!=367874||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=18)return false;
}
{const Command&c=_programs[1][4];if(c.opcode!=17||c.delay!=-1||c.offset!=367886||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=19)return false;
}
{const Command&c=_programs[1][5];if(c.opcode!=17||c.delay!=-1||c.offset!=367898||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=20)return false;
}
{const Command&c=_programs[1][6];if(c.opcode!=17||c.delay!=-1||c.offset!=367910||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=21)return false;
}
{const Command&c=_programs[1][7];if(c.opcode!=17||c.delay!=-1||c.offset!=367922||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=22)return false;
}
if(_programs[2].size()!=45)return false;
{const Command&c=_programs[2][0];if(c.opcode!=31||c.delay!=0||c.offset!=367938||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=4)return false;
if(c.args[2]!=1)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[2][1];if(c.opcode!=20||c.delay!=-1||c.offset!=367970||c.args.size()!=2||c.text!="mooncor")return false;
if(c.args[0]!=79)return false;
if(c.args[1]!=358)return false;
}
{const Command&c=_programs[2][2];if(c.opcode!=49||c.delay!=-1||c.offset!=368241||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[2][3];if(c.opcode!=16||c.delay!=0||c.offset!=368249||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=16)return false;
}
{const Command&c=_programs[2][4];if(c.opcode!=37||c.delay!=0||c.offset!=368261||c.args.size()!=3||c.text!="")return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=150)return false;
}
{const Command&c=_programs[2][5];if(c.opcode!=36||c.delay!=0||c.offset!=368281||c.args.size()!=2||c.text!="")return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=0)return false;
}
{const Command&c=_programs[2][6];if(c.opcode!=45||c.delay!=-1||c.offset!=368297||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[2][7];if(c.opcode!=31||c.delay!=0||c.offset!=368305||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=4)return false;
if(c.args[2]!=2)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[2][8];if(c.opcode!=20||c.delay!=-1||c.offset!=368337||c.args.size()!=2||c.text!="moonhalo")return false;
if(c.args[0]!=79)return false;
if(c.args[1]!=358)return false;
}
{const Command&c=_programs[2][9];if(c.opcode!=49||c.delay!=-1||c.offset!=368608||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[2][10];if(c.opcode!=16||c.delay!=0||c.offset!=368616||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=17)return false;
}
{const Command&c=_programs[2][11];if(c.opcode!=37||c.delay!=0||c.offset!=368628||c.args.size()!=3||c.text!="")return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=150)return false;
if(c.args[2]!=204)return false;
}
{const Command&c=_programs[2][12];if(c.opcode!=36||c.delay!=0||c.offset!=368648||c.args.size()!=2||c.text!="")return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=150)return false;
}
{const Command&c=_programs[2][13];if(c.opcode!=45||c.delay!=-1||c.offset!=368664||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[2][14];if(c.opcode!=31||c.delay!=0||c.offset!=368672||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=4)return false;
if(c.args[2]!=3)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[2][15];if(c.opcode!=20||c.delay!=-1||c.offset!=368704||c.args.size()!=2||c.text!="sundogs")return false;
if(c.args[0]!=79)return false;
if(c.args[1]!=358)return false;
}
{const Command&c=_programs[2][16];if(c.opcode!=49||c.delay!=-1||c.offset!=368975||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[2][17];if(c.opcode!=16||c.delay!=0||c.offset!=368983||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=20)return false;
}
{const Command&c=_programs[2][18];if(c.opcode!=37||c.delay!=0||c.offset!=368995||c.args.size()!=3||c.text!="")return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=1272)return false;
if(c.args[2]!=184)return false;
}
{const Command&c=_programs[2][19];if(c.opcode!=36||c.delay!=0||c.offset!=369015||c.args.size()!=2||c.text!="")return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=1272)return false;
}
{const Command&c=_programs[2][20];if(c.opcode!=45||c.delay!=-1||c.offset!=369031||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[2][21];if(c.opcode!=31||c.delay!=0||c.offset!=369039||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=4)return false;
if(c.args[2]!=4)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[2][22];if(c.opcode!=20||c.delay!=-1||c.offset!=369071||c.args.size()!=2||c.text!="sunhalo")return false;
if(c.args[0]!=79)return false;
if(c.args[1]!=358)return false;
}
{const Command&c=_programs[2][23];if(c.opcode!=49||c.delay!=-1||c.offset!=369342||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[2][24];if(c.opcode!=16||c.delay!=0||c.offset!=369350||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=21)return false;
}
{const Command&c=_programs[2][25];if(c.opcode!=37||c.delay!=0||c.offset!=369362||c.args.size()!=3||c.text!="")return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=1456)return false;
if(c.args[2]!=186)return false;
}
{const Command&c=_programs[2][26];if(c.opcode!=36||c.delay!=0||c.offset!=369382||c.args.size()!=2||c.text!="")return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=1456)return false;
}
{const Command&c=_programs[2][27];if(c.opcode!=45||c.delay!=-1||c.offset!=369398||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[2][28];if(c.opcode!=31||c.delay!=0||c.offset!=369406||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=4)return false;
if(c.args[2]!=5)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[2][29];if(c.opcode!=20||c.delay!=-1||c.offset!=369438||c.args.size()!=2||c.text!="sunpill")return false;
if(c.args[0]!=79)return false;
if(c.args[1]!=358)return false;
}
{const Command&c=_programs[2][30];if(c.opcode!=49||c.delay!=-1||c.offset!=369709||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[2][31];if(c.opcode!=16||c.delay!=0||c.offset!=369717||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=22)return false;
}
{const Command&c=_programs[2][32];if(c.opcode!=37||c.delay!=0||c.offset!=369729||c.args.size()!=3||c.text!="")return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=1642)return false;
if(c.args[2]!=189)return false;
}
{const Command&c=_programs[2][33];if(c.opcode!=36||c.delay!=0||c.offset!=369749||c.args.size()!=2||c.text!="")return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=1642)return false;
}
{const Command&c=_programs[2][34];if(c.opcode!=45||c.delay!=-1||c.offset!=369765||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[2][35];if(c.opcode!=31||c.delay!=0||c.offset!=369773||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=4)return false;
if(c.args[2]!=6)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[2][36];if(c.opcode!=20||c.delay!=-1||c.offset!=369805||c.args.size()!=2||c.text!="creprays")return false;
if(c.args[0]!=79)return false;
if(c.args[1]!=358)return false;
}
{const Command&c=_programs[2][37];if(c.opcode!=49||c.delay!=-1||c.offset!=370076||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[2][38];if(c.opcode!=16||c.delay!=0||c.offset!=370084||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=15)return false;
}
{const Command&c=_programs[2][39];if(c.opcode!=37||c.delay!=0||c.offset!=370096||c.args.size()!=3||c.text!="")return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=1834)return false;
if(c.args[2]!=85)return false;
}
{const Command&c=_programs[2][40];if(c.opcode!=36||c.delay!=0||c.offset!=370116||c.args.size()!=2||c.text!="")return false;
if(c.args[0]!=0)return false;
if(c.args[1]!=1834)return false;
}
{const Command&c=_programs[2][41];if(c.opcode!=42||c.delay!=-1||c.offset!=370132||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[2][42];if(c.opcode!=23||c.delay!=0||c.offset!=370140||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=24)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=160)return false;
if(c.args[3]!=57)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[2][43];if(c.opcode!=23||c.delay!=0||c.offset!=370172||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=24)return false;
if(c.args[1]!=3)return false;
if(c.args[2]!=160)return false;
if(c.args[3]!=57)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[2][44];if(c.opcode!=29||c.delay!=150||c.offset!=370204||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=-1)return false;
}
if(_programs[3].size()!=62)return false;
{const Command&c=_programs[3][0];if(c.opcode!=31||c.delay!=0||c.offset!=370220||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=15)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][1];if(c.opcode!=16||c.delay!=-1||c.offset!=370252||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=36)return false;
}
{const Command&c=_programs[3][2];if(c.opcode!=45||c.delay!=-1||c.offset!=370264||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][3];if(c.opcode!=31||c.delay!=-1||c.offset!=370272||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=14)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][4];if(c.opcode!=17||c.delay!=-1||c.offset!=370304||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=36)return false;
}
{const Command&c=_programs[3][5];if(c.opcode!=16||c.delay!=-1||c.offset!=370316||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=35)return false;
}
{const Command&c=_programs[3][6];if(c.opcode!=45||c.delay!=-1||c.offset!=370328||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][7];if(c.opcode!=31||c.delay!=-1||c.offset!=370336||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=13)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][8];if(c.opcode!=17||c.delay!=-1||c.offset!=370368||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=35)return false;
}
{const Command&c=_programs[3][9];if(c.opcode!=16||c.delay!=-1||c.offset!=370380||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=34)return false;
}
{const Command&c=_programs[3][10];if(c.opcode!=45||c.delay!=-1||c.offset!=370392||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][11];if(c.opcode!=31||c.delay!=-1||c.offset!=370400||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=12)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][12];if(c.opcode!=17||c.delay!=-1||c.offset!=370432||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=34)return false;
}
{const Command&c=_programs[3][13];if(c.opcode!=16||c.delay!=-1||c.offset!=370444||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=33)return false;
}
{const Command&c=_programs[3][14];if(c.opcode!=45||c.delay!=-1||c.offset!=370456||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][15];if(c.opcode!=31||c.delay!=-1||c.offset!=370464||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=11)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][16];if(c.opcode!=17||c.delay!=-1||c.offset!=370496||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=33)return false;
}
{const Command&c=_programs[3][17];if(c.opcode!=16||c.delay!=-1||c.offset!=370508||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=32)return false;
}
{const Command&c=_programs[3][18];if(c.opcode!=45||c.delay!=-1||c.offset!=370520||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][19];if(c.opcode!=31||c.delay!=-1||c.offset!=370528||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=10)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][20];if(c.opcode!=17||c.delay!=-1||c.offset!=370560||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=32)return false;
}
{const Command&c=_programs[3][21];if(c.opcode!=16||c.delay!=-1||c.offset!=370572||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=31)return false;
}
{const Command&c=_programs[3][22];if(c.opcode!=45||c.delay!=-1||c.offset!=370584||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][23];if(c.opcode!=31||c.delay!=-1||c.offset!=370592||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=9)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][24];if(c.opcode!=17||c.delay!=-1||c.offset!=370624||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=31)return false;
}
{const Command&c=_programs[3][25];if(c.opcode!=16||c.delay!=-1||c.offset!=370636||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=30)return false;
}
{const Command&c=_programs[3][26];if(c.opcode!=45||c.delay!=-1||c.offset!=370648||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][27];if(c.opcode!=31||c.delay!=-1||c.offset!=370656||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=8)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][28];if(c.opcode!=17||c.delay!=-1||c.offset!=370688||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=30)return false;
}
{const Command&c=_programs[3][29];if(c.opcode!=16||c.delay!=-1||c.offset!=370700||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=29)return false;
}
{const Command&c=_programs[3][30];if(c.opcode!=45||c.delay!=-1||c.offset!=370712||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][31];if(c.opcode!=31||c.delay!=-1||c.offset!=370720||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=7)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][32];if(c.opcode!=17||c.delay!=-1||c.offset!=370752||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=29)return false;
}
{const Command&c=_programs[3][33];if(c.opcode!=16||c.delay!=-1||c.offset!=370764||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=28)return false;
}
{const Command&c=_programs[3][34];if(c.opcode!=45||c.delay!=-1||c.offset!=370776||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][35];if(c.opcode!=31||c.delay!=-1||c.offset!=370784||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=6)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][36];if(c.opcode!=17||c.delay!=-1||c.offset!=370816||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=28)return false;
}
{const Command&c=_programs[3][37];if(c.opcode!=16||c.delay!=-1||c.offset!=370828||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=27)return false;
}
{const Command&c=_programs[3][38];if(c.opcode!=45||c.delay!=-1||c.offset!=370840||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][39];if(c.opcode!=31||c.delay!=-1||c.offset!=370848||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=5)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][40];if(c.opcode!=17||c.delay!=-1||c.offset!=370880||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=27)return false;
}
{const Command&c=_programs[3][41];if(c.opcode!=16||c.delay!=-1||c.offset!=370892||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=26)return false;
}
{const Command&c=_programs[3][42];if(c.opcode!=45||c.delay!=-1||c.offset!=370904||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][43];if(c.opcode!=31||c.delay!=-1||c.offset!=370912||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=4)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][44];if(c.opcode!=17||c.delay!=-1||c.offset!=370944||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=26)return false;
}
{const Command&c=_programs[3][45];if(c.opcode!=16||c.delay!=-1||c.offset!=370956||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=25)return false;
}
{const Command&c=_programs[3][46];if(c.opcode!=45||c.delay!=-1||c.offset!=370968||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][47];if(c.opcode!=31||c.delay!=-1||c.offset!=370976||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=3)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][48];if(c.opcode!=17||c.delay!=-1||c.offset!=371008||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=25)return false;
}
{const Command&c=_programs[3][49];if(c.opcode!=16||c.delay!=-1||c.offset!=371020||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=24)return false;
}
{const Command&c=_programs[3][50];if(c.opcode!=45||c.delay!=-1||c.offset!=371032||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][51];if(c.opcode!=31||c.delay!=-1||c.offset!=371040||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=2)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][52];if(c.opcode!=17||c.delay!=-1||c.offset!=371072||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=24)return false;
}
{const Command&c=_programs[3][53];if(c.opcode!=16||c.delay!=-1||c.offset!=371084||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=23)return false;
}
{const Command&c=_programs[3][54];if(c.opcode!=45||c.delay!=-1||c.offset!=371096||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][55];if(c.opcode!=31||c.delay!=-1||c.offset!=371104||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=1)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][56];if(c.opcode!=17||c.delay!=-1||c.offset!=371136||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=23)return false;
}
{const Command&c=_programs[3][57];if(c.opcode!=16||c.delay!=-1||c.offset!=371148||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=7)return false;
}
{const Command&c=_programs[3][58];if(c.opcode!=45||c.delay!=-1||c.offset!=371160||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[3][59];if(c.opcode!=31||c.delay!=-1||c.offset!=371168||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=0)return false;
if(c.args[2]!=0)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[3][60];if(c.opcode!=17||c.delay!=-1||c.offset!=371200||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=7)return false;
}
{const Command&c=_programs[3][61];if(c.opcode!=42||c.delay!=-1||c.offset!=371212||c.args.size()!=0||c.text!="")return false;
}
if(_programs[4].size()!=62)return false;
{const Command&c=_programs[4][0];if(c.opcode!=31||c.delay!=0||c.offset!=371224||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=15)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][1];if(c.opcode!=16||c.delay!=-1||c.offset!=371256||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=50)return false;
}
{const Command&c=_programs[4][2];if(c.opcode!=45||c.delay!=-1||c.offset!=371268||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][3];if(c.opcode!=31||c.delay!=-1||c.offset!=371276||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=14)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][4];if(c.opcode!=17||c.delay!=-1||c.offset!=371308||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=50)return false;
}
{const Command&c=_programs[4][5];if(c.opcode!=16||c.delay!=-1||c.offset!=371320||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=49)return false;
}
{const Command&c=_programs[4][6];if(c.opcode!=45||c.delay!=-1||c.offset!=371332||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][7];if(c.opcode!=31||c.delay!=-1||c.offset!=371340||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=13)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][8];if(c.opcode!=17||c.delay!=-1||c.offset!=371372||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=49)return false;
}
{const Command&c=_programs[4][9];if(c.opcode!=16||c.delay!=-1||c.offset!=371384||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=48)return false;
}
{const Command&c=_programs[4][10];if(c.opcode!=45||c.delay!=-1||c.offset!=371396||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][11];if(c.opcode!=31||c.delay!=-1||c.offset!=371404||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=12)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][12];if(c.opcode!=17||c.delay!=-1||c.offset!=371436||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=48)return false;
}
{const Command&c=_programs[4][13];if(c.opcode!=16||c.delay!=-1||c.offset!=371448||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=47)return false;
}
{const Command&c=_programs[4][14];if(c.opcode!=45||c.delay!=-1||c.offset!=371460||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][15];if(c.opcode!=31||c.delay!=-1||c.offset!=371468||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=11)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][16];if(c.opcode!=17||c.delay!=-1||c.offset!=371500||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=47)return false;
}
{const Command&c=_programs[4][17];if(c.opcode!=16||c.delay!=-1||c.offset!=371512||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=46)return false;
}
{const Command&c=_programs[4][18];if(c.opcode!=45||c.delay!=-1||c.offset!=371524||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][19];if(c.opcode!=31||c.delay!=-1||c.offset!=371532||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=10)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][20];if(c.opcode!=17||c.delay!=-1||c.offset!=371564||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=46)return false;
}
{const Command&c=_programs[4][21];if(c.opcode!=16||c.delay!=-1||c.offset!=371576||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=45)return false;
}
{const Command&c=_programs[4][22];if(c.opcode!=45||c.delay!=-1||c.offset!=371588||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][23];if(c.opcode!=31||c.delay!=-1||c.offset!=371596||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=9)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][24];if(c.opcode!=17||c.delay!=-1||c.offset!=371628||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=45)return false;
}
{const Command&c=_programs[4][25];if(c.opcode!=16||c.delay!=-1||c.offset!=371640||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=44)return false;
}
{const Command&c=_programs[4][26];if(c.opcode!=45||c.delay!=-1||c.offset!=371652||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][27];if(c.opcode!=31||c.delay!=-1||c.offset!=371660||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=8)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][28];if(c.opcode!=17||c.delay!=-1||c.offset!=371692||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=44)return false;
}
{const Command&c=_programs[4][29];if(c.opcode!=16||c.delay!=-1||c.offset!=371704||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=43)return false;
}
{const Command&c=_programs[4][30];if(c.opcode!=45||c.delay!=-1||c.offset!=371716||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][31];if(c.opcode!=31||c.delay!=-1||c.offset!=371724||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=7)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][32];if(c.opcode!=17||c.delay!=-1||c.offset!=371756||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=43)return false;
}
{const Command&c=_programs[4][33];if(c.opcode!=16||c.delay!=-1||c.offset!=371768||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=42)return false;
}
{const Command&c=_programs[4][34];if(c.opcode!=45||c.delay!=-1||c.offset!=371780||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][35];if(c.opcode!=31||c.delay!=-1||c.offset!=371788||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=6)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][36];if(c.opcode!=17||c.delay!=-1||c.offset!=371820||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=42)return false;
}
{const Command&c=_programs[4][37];if(c.opcode!=16||c.delay!=-1||c.offset!=371832||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=41)return false;
}
{const Command&c=_programs[4][38];if(c.opcode!=45||c.delay!=-1||c.offset!=371844||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][39];if(c.opcode!=31||c.delay!=-1||c.offset!=371852||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=5)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][40];if(c.opcode!=17||c.delay!=-1||c.offset!=371884||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=41)return false;
}
{const Command&c=_programs[4][41];if(c.opcode!=16||c.delay!=-1||c.offset!=371896||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=40)return false;
}
{const Command&c=_programs[4][42];if(c.opcode!=45||c.delay!=-1||c.offset!=371908||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][43];if(c.opcode!=31||c.delay!=-1||c.offset!=371916||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=4)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][44];if(c.opcode!=17||c.delay!=-1||c.offset!=371948||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=40)return false;
}
{const Command&c=_programs[4][45];if(c.opcode!=16||c.delay!=-1||c.offset!=371960||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=39)return false;
}
{const Command&c=_programs[4][46];if(c.opcode!=45||c.delay!=-1||c.offset!=371972||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][47];if(c.opcode!=31||c.delay!=-1||c.offset!=371980||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=3)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][48];if(c.opcode!=17||c.delay!=-1||c.offset!=372012||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=39)return false;
}
{const Command&c=_programs[4][49];if(c.opcode!=16||c.delay!=-1||c.offset!=372024||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=38)return false;
}
{const Command&c=_programs[4][50];if(c.opcode!=45||c.delay!=-1||c.offset!=372036||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][51];if(c.opcode!=31||c.delay!=-1||c.offset!=372044||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=2)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][52];if(c.opcode!=17||c.delay!=-1||c.offset!=372076||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=38)return false;
}
{const Command&c=_programs[4][53];if(c.opcode!=16||c.delay!=-1||c.offset!=372088||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=37)return false;
}
{const Command&c=_programs[4][54];if(c.opcode!=45||c.delay!=-1||c.offset!=372100||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][55];if(c.opcode!=31||c.delay!=-1||c.offset!=372108||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=1)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][56];if(c.opcode!=17||c.delay!=-1||c.offset!=372140||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=37)return false;
}
{const Command&c=_programs[4][57];if(c.opcode!=16||c.delay!=-1||c.offset!=372152||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=10)return false;
}
{const Command&c=_programs[4][58];if(c.opcode!=45||c.delay!=-1||c.offset!=372164||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[4][59];if(c.opcode!=31||c.delay!=-1||c.offset!=372172||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=1)return false;
if(c.args[2]!=0)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[4][60];if(c.opcode!=17||c.delay!=-1||c.offset!=372204||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=10)return false;
}
{const Command&c=_programs[4][61];if(c.opcode!=42||c.delay!=-1||c.offset!=372216||c.args.size()!=0||c.text!="")return false;
}
if(_programs[5].size()!=62)return false;
{const Command&c=_programs[5][0];if(c.opcode!=31||c.delay!=0||c.offset!=372228||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=15)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][1];if(c.opcode!=16||c.delay!=-1||c.offset!=372260||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=64)return false;
}
{const Command&c=_programs[5][2];if(c.opcode!=45||c.delay!=-1||c.offset!=372272||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][3];if(c.opcode!=31||c.delay!=-1||c.offset!=372280||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=14)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][4];if(c.opcode!=17||c.delay!=-1||c.offset!=372312||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=64)return false;
}
{const Command&c=_programs[5][5];if(c.opcode!=16||c.delay!=-1||c.offset!=372324||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=63)return false;
}
{const Command&c=_programs[5][6];if(c.opcode!=45||c.delay!=-1||c.offset!=372336||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][7];if(c.opcode!=31||c.delay!=-1||c.offset!=372344||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=13)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][8];if(c.opcode!=17||c.delay!=-1||c.offset!=372376||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=63)return false;
}
{const Command&c=_programs[5][9];if(c.opcode!=16||c.delay!=-1||c.offset!=372388||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=62)return false;
}
{const Command&c=_programs[5][10];if(c.opcode!=45||c.delay!=-1||c.offset!=372400||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][11];if(c.opcode!=31||c.delay!=-1||c.offset!=372408||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=12)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][12];if(c.opcode!=17||c.delay!=-1||c.offset!=372440||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=62)return false;
}
{const Command&c=_programs[5][13];if(c.opcode!=16||c.delay!=-1||c.offset!=372452||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=61)return false;
}
{const Command&c=_programs[5][14];if(c.opcode!=45||c.delay!=-1||c.offset!=372464||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][15];if(c.opcode!=31||c.delay!=-1||c.offset!=372472||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=11)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][16];if(c.opcode!=17||c.delay!=-1||c.offset!=372504||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=61)return false;
}
{const Command&c=_programs[5][17];if(c.opcode!=16||c.delay!=-1||c.offset!=372516||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=60)return false;
}
{const Command&c=_programs[5][18];if(c.opcode!=45||c.delay!=-1||c.offset!=372528||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][19];if(c.opcode!=31||c.delay!=-1||c.offset!=372536||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=10)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][20];if(c.opcode!=17||c.delay!=-1||c.offset!=372568||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=60)return false;
}
{const Command&c=_programs[5][21];if(c.opcode!=16||c.delay!=-1||c.offset!=372580||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=59)return false;
}
{const Command&c=_programs[5][22];if(c.opcode!=45||c.delay!=-1||c.offset!=372592||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][23];if(c.opcode!=31||c.delay!=-1||c.offset!=372600||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=9)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][24];if(c.opcode!=17||c.delay!=-1||c.offset!=372632||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=59)return false;
}
{const Command&c=_programs[5][25];if(c.opcode!=16||c.delay!=-1||c.offset!=372644||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=58)return false;
}
{const Command&c=_programs[5][26];if(c.opcode!=45||c.delay!=-1||c.offset!=372656||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][27];if(c.opcode!=31||c.delay!=-1||c.offset!=372664||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=8)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][28];if(c.opcode!=17||c.delay!=-1||c.offset!=372696||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=58)return false;
}
{const Command&c=_programs[5][29];if(c.opcode!=16||c.delay!=-1||c.offset!=372708||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=57)return false;
}
{const Command&c=_programs[5][30];if(c.opcode!=45||c.delay!=-1||c.offset!=372720||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][31];if(c.opcode!=31||c.delay!=-1||c.offset!=372728||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=7)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][32];if(c.opcode!=17||c.delay!=-1||c.offset!=372760||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=57)return false;
}
{const Command&c=_programs[5][33];if(c.opcode!=16||c.delay!=-1||c.offset!=372772||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=56)return false;
}
{const Command&c=_programs[5][34];if(c.opcode!=45||c.delay!=-1||c.offset!=372784||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][35];if(c.opcode!=31||c.delay!=-1||c.offset!=372792||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=6)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][36];if(c.opcode!=17||c.delay!=-1||c.offset!=372824||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=56)return false;
}
{const Command&c=_programs[5][37];if(c.opcode!=16||c.delay!=-1||c.offset!=372836||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=55)return false;
}
{const Command&c=_programs[5][38];if(c.opcode!=45||c.delay!=-1||c.offset!=372848||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][39];if(c.opcode!=31||c.delay!=-1||c.offset!=372856||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=5)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][40];if(c.opcode!=17||c.delay!=-1||c.offset!=372888||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=55)return false;
}
{const Command&c=_programs[5][41];if(c.opcode!=16||c.delay!=-1||c.offset!=372900||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=54)return false;
}
{const Command&c=_programs[5][42];if(c.opcode!=45||c.delay!=-1||c.offset!=372912||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][43];if(c.opcode!=31||c.delay!=-1||c.offset!=372920||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=4)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][44];if(c.opcode!=17||c.delay!=-1||c.offset!=372952||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=54)return false;
}
{const Command&c=_programs[5][45];if(c.opcode!=16||c.delay!=-1||c.offset!=372964||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=53)return false;
}
{const Command&c=_programs[5][46];if(c.opcode!=45||c.delay!=-1||c.offset!=372976||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][47];if(c.opcode!=31||c.delay!=-1||c.offset!=372984||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=3)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][48];if(c.opcode!=17||c.delay!=-1||c.offset!=373016||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=53)return false;
}
{const Command&c=_programs[5][49];if(c.opcode!=16||c.delay!=-1||c.offset!=373028||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=52)return false;
}
{const Command&c=_programs[5][50];if(c.opcode!=45||c.delay!=-1||c.offset!=373040||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][51];if(c.opcode!=31||c.delay!=-1||c.offset!=373048||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=2)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][52];if(c.opcode!=17||c.delay!=-1||c.offset!=373080||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=52)return false;
}
{const Command&c=_programs[5][53];if(c.opcode!=16||c.delay!=-1||c.offset!=373092||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=51)return false;
}
{const Command&c=_programs[5][54];if(c.opcode!=45||c.delay!=-1||c.offset!=373104||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][55];if(c.opcode!=31||c.delay!=-1||c.offset!=373112||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=1)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][56];if(c.opcode!=17||c.delay!=-1||c.offset!=373144||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=51)return false;
}
{const Command&c=_programs[5][57];if(c.opcode!=16||c.delay!=-1||c.offset!=373156||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=13)return false;
}
{const Command&c=_programs[5][58];if(c.opcode!=45||c.delay!=-1||c.offset!=373168||c.args.size()!=0||c.text!="")return false;
}
{const Command&c=_programs[5][59];if(c.opcode!=31||c.delay!=-1||c.offset!=373176||c.args.size()!=6||c.text!="")return false;
if(c.args[0]!=1)return false;
if(c.args[1]!=2)return false;
if(c.args[2]!=0)return false;
if(c.args[3]!=0)return false;
if(c.args[4]!=0)return false;
if(c.args[5]!=0)return false;
}
{const Command&c=_programs[5][60];if(c.opcode!=17||c.delay!=-1||c.offset!=373208||c.args.size()!=1||c.text!="")return false;
if(c.args[0]!=13)return false;
}
{const Command&c=_programs[5][61];if(c.opcode!=42||c.delay!=-1||c.offset!=373220||c.args.size()!=0||c.text!="")return false;
}
return true;}
bool ScriptRunner::validP512SettledValues(const Common::Array<uint32>&w)const{
 if(!validPersistentState(w))return false;const uint widths[]={20,20,20,6,6,1};
 for(uint i=0;i<100;++i){if(w[3*i+2]!=1||(w[3*i+1]&&(i>=3||w[3*i+1]!=6)))return false;if(w[301+3*i]!=(i<6?widths[i]:0U)||w[302+3*i]!=uint32(i<6))return false;}
 if(w[300]>15||w[303]>15||w[306]>15||!w[309]||(w[309]>63&&w[309]!=127)||w[312]<1||w[312]>6||w[315]>1)return false;
 return (w[309]&(1U<<(w[312]-1)))!=0;
}
bool ScriptRunner::exportP512SettledState(Common::Array<uint32>&words)const{
 if(!trustedP512SettledProgram()||!scriptsIdle())return false;Common::Array<uint32>w;if(!exportPersistentState(w)||!validP512SettledValues(w))return false;words=w;return true;
}
bool ScriptRunner::importP512SettledState(const Common::Array<uint32>&words){
 if(!trustedP512SettledProgram()||!scriptsIdle()||!validP512SettledValues(words))return false;return importPersistentState(words);
}
bool ScriptRunner::testP512SettledState(uint32 now)const{
 Common::Array<uint32>w;if(!exportP512SettledState(w))return false;ScriptRunner prepared=*this;if(!prepared.importP512SettledState(w)||prepared.probeDiagnosticHash(false)!=probeDiagnosticHash(false))return false;Common::Array<uint32>again;if(!prepared.exportP512SettledState(again)||again!=w)return false;
 for(uint program:{3U,4U,5U}){ScriptRunner expected=*this,actual=prepared;if(!expected.enqueue(_programs[program],now,true)||!actual.enqueue(_programs[program],now,true))return false;for(uint32 at:{now,now+1,now+150,now+500}){expected.tick(at);actual.tick(at);if(expected.probeDiagnosticHash(false)!=actual.probeDiagnosticHash(false))return false;}}
 const uint offsets[]={1,2,300,301,302,303,306,309,310,311,312,315,319,320,602,603,604};for(uint offset:offsets){Common::Array<uint32>bad=w;bad[offset]=0xffffffffU;ScriptRunner target=*this;const uint32 before=target.probeDiagnosticHash(true);if(target.importP512SettledState(bad)||target.probeDiagnosticHash(true)!=before)return false;}
 for(uint badMask:{0U,64U,128U}){Common::Array<uint32>bad=w;bad[309]=badMask;ScriptRunner target=*this;const uint32 before=target.probeDiagnosticHash(true);if(target.importP512SettledState(bad)||target.probeDiagnosticHash(true)!=before)return false;}
 {Common::Array<uint32>bad=w;bad[309]&=~(1U<<(bad[312]-1));ScriptRunner target=*this;const uint32 before=target.probeDiagnosticHash(true);if(target.importP512SettledState(bad)||target.probeDiagnosticHash(true)!=before)return false;}
 for(uint kind=0;kind<4;++kind){ScriptRunner bad=*this;if(kind==0)bad._weatherSupport=false;if(kind==1)bad._programs[2][4].delay=1;if(kind==2)bad._pending.push_back(Pending{_programs[3],0,now});if(kind==3)bad._actions.push_back(Action{});Common::Array<uint32>out;out.push_back(123456);const uint32 before=bad.probeDiagnosticHash(true);if(bad.exportP512SettledState(out)||out.size()!=1||out[0]!=123456||bad.probeDiagnosticHash(true)!=before)return false;}
 debug("P512 settled runner preflight: PASS (605 words,3 original redraw futures,21 invalid states,4 export exclusions)");return true;
}

void ScriptRunner::p512AuditExportState(Common::Array<uint32>&words)const{exportSettledValues(words);words.push_back(_variantRound);words.push_back(_variantMask);}
void ScriptRunner::p512AuditPending(uint row,uint32 now)const{
 debug("P512QUEUE row=%u now=%u loaded=%u pending=%u actions=%u blocked=%u",row,now,_programLoadedAt,_pending.size(),_actions.size(),uint(_clicksBlocked));
 for(uint i=0;i<_pending.size();++i){const Pending&p=_pending[i];int program=-1;for(uint j=0;j<_programs.size();++j)if(p.script.size()==_programs[j].size()){bool same=true;for(uint k=0;k<p.script.size();++k){const Command&a=p.script[k],&b=_programs[j][k];same&=a.opcode==b.opcode&&a.delay==b.delay&&a.args==b.args&&a.text==b.text;}if(same)program=j;}debug("P512PENDING row=%u program=%d index=%u since=%u count=%u",row,program,p.index,p.since,p.script.size());}
}


uint32 ScriptRunner::probeDiagnosticHash(bool strict) const {
 uint32 h=2166136261U;auto add=[&](uint32 v){h=(h^v)*16777619U;};Common::Array<uint32>w;exportSettledValues(w);for(uint32 v:w)add(v);add(_variantRound);add(_variantMask);add(_clicksBlocked);add(_pending.size());add(_actions.size());
 for(const Pending&p:_pending){add(p.index);add(p.since);add(p.script.size());for(const Command&c:p.script){add(c.opcode);add(c.delay);add(c.args.size());for(int32 v:c.args)add(v);}}
 for(const Action&a:_actions){add(a.opcode);add(a.value);add(a.x);add(a.y);for(char c:a.text)add(byte(c));for(int32 v:a.motion)add(v);}
 if(strict){add(_pendingEpoch);add(_executed);add(_spriteTargets.size());for(uint v:_spriteTargets)add(v);add(_soundTargets.size());for(bool v:_soundTargets)add(v);add(_gameStateHandler!=nullptr);add(_soundHandler!=nullptr);add(_probeHandler!=nullptr);add(_successHandler!=nullptr);}return h;
}

bool ScriptRunner::trustedProbePollProgram() const {
 if (!_probeHandler || _programs.size() != 11 || _programs[0].size() != 7) return false;
 const Command &last = _programs[0][6];
 return last.opcode == 41 && last.delay == 200 && last.args.size() == 1 && last.args[0] == 0;
}
bool ScriptRunner::exportProbePollState(Common::Array<uint32> &words, uint32 &since) const {
 if (!trustedProbePollProgram() || _pending.size() != 1 || !_actions.empty() || _clicksBlocked) return false;
 const Pending &p = _pending[0];
 if (p.index != 6 || p.script.size() != _programs[0].size()) return false;
 for (uint i = 0; i < p.script.size(); ++i)
  if (p.script[i].opcode != _programs[0][i].opcode || p.script[i].delay != _programs[0][i].delay || p.script[i].args != _programs[0][i].args) return false;
 Common::Array<uint32> state; exportSettledValues(state); state.push_back(_variantRound); state.push_back(_variantMask);
 if (!validPersistentState(state) || state[300] < 1 || state[300] > 4 || state[303] != 0) return false;
 words = state; since = p.since; return true;
}
bool ScriptRunner::importProbePollState(const Common::Array<uint32> &words, uint32 since) {
 if (!trustedProbePollProgram() || !scriptsIdle() || !validPersistentState(words) || words[300] < 1 || words[300] > 4 || words[303] != 0) return false;
 // Match declarations from the already loaded trusted scene, including unknown
 // slots; do not invent zero values for retained undeclared local data.
 for (uint i = 0; i < 100; ++i)
  if (words[301+3*i] != uint32(_widths[1][i]) || words[302+3*i] != uint32(_known[1][i])) return false;
 importSettledValues(words); _variantRound = words[603]; _variantMask = words[604];
 _pending.push_back(Pending{_programs[0],6,since}); ++_pendingEpoch; return true;
}
bool ScriptRunner::verifyProbePollSnapshots() const {
 Common::Array<uint32> saved; uint32 originalSince = 0;
 if (!exportProbePollState(saved,originalSince)) return false;
 uint cases = 0, rejected = 0;
 for (uint32 epoch : {originalSince,0xfffffff0U}) for (uint32 age : {0U,1U,199U,200U,201U,210U,1000U}) {
  ScriptRunner expected = *this, actual = *this;
  expected._pending[0].since = epoch; actual.clear();
  if (!actual.importProbePollState(saved,epoch)) return false;
  Common::Array<uint32> again; uint32 restored = 0;
  if (!actual.exportProbePollState(again,restored) || again != saved || restored != epoch) return false;
  const uint32 now = epoch+age;
  auto equivalent = [&]() {
   Common::Array<uint32> a,b; expected.exportSettledValues(a); actual.exportSettledValues(b);
   if (a != b || expected._variantRound != actual._variantRound || expected._variantMask != actual._variantMask || expected._pending.size() != actual._pending.size() || expected._actions.size() != actual._actions.size() || expected._clicksBlocked != actual._clicksBlocked) return false;
   for (uint i = 0; i < expected._pending.size(); ++i) {
    const Pending &x = expected._pending[i],&y = actual._pending[i];
    if (x.index != y.index || x.since != y.since || x.script.size() != y.script.size()) return false;
    for (uint j = 0; j < x.script.size(); ++j)
     if (x.script[j].opcode != y.script[j].opcode || x.script[j].delay != y.script[j].delay || x.script[j].args != y.script[j].args) return false;
   }
   return true;
  };
  expected.tick(now); actual.tick(now);
  if (!equivalent() || actual._pending.size() != 1 || actual._pending[0].index != (age >= 200 ? 0U : 6U)) return false;
  if (age >= 200 && actual.exportProbePollState(again,restored)) return false;
  // opcode41 queues program0 for another pass; it must not execute immediately.
  expected.tick(now); actual.tick(now);
  if (!equivalent() || !actual.exportProbePollState(again,restored) || restored != (age >= 200 ? now : epoch)) return false;
  expected.tick(now+199); actual.tick(now+199); if (!equivalent()) return false;
  expected.tick(now+199); actual.tick(now+199);
  if (!equivalent() || !actual.exportProbePollState(again,restored)) return false;
  const bool dueAgain = int32(now+200-actual._pending[0].since) >= 200;
  expected.tick(now+200); actual.tick(now+200); if (!equivalent()) return false;
  if (actual.exportProbePollState(again,restored) == dueAgain) return false;
  expected.tick(now+200); actual.tick(now+200);
  if (!equivalent() || !actual.exportProbePollState(again,restored)) return false;

  ++cases;
 }
 auto denied = [&](Common::Array<uint32> bad) {
  ScriptRunner target = *this; target.clear();
  Common::Array<uint32> before,after; target.exportSettledValues(before);
  const uint round = target._variantRound,mask = target._variantMask,generation = target._pendingEpoch;
  if (target.importProbePollState(bad,originalSince)) return false;
  target.exportSettledValues(after);
  if (before != after || !target.scriptsIdle() || target._variantRound != round || target._variantMask != mask || target._pendingEpoch != generation) return false;
  ++rejected; return true;
 };
 for (uint field : {2U,300U,301U,302U,303U,602U,603U,604U}) {
  Common::Array<uint32> bad = saved; bad[field] = 0xffffffffU; if (!denied(bad)) return false;
 }
 Common::Array<uint32> shortState = saved; shortState.resize(604); if (!denied(shortState)) return false;
 for (uint mutation = 0; mutation < 5; ++mutation) {
  ScriptRunner bad = *this;
  if (mutation == 0) bad._pending.push_back(bad._pending[0]);
  if (mutation == 1) bad._pending[0].index = 5;
  if (mutation == 2) bad._pending[0].script[6].delay = 201;
  if (mutation == 3) bad._clicksBlocked = true;
  if (mutation == 4) bad._actions.push_back(Action{});
  Common::Array<uint32> out; uint32 when = 0;
  if (bad.exportProbePollState(out,when)) return false;
  ++rejected;
 }
 debug("Astronomica probe poll snapshot kernel: PASS (%u timing cases, %u atomic/shape rejections; original605 words, retained epoch, wrap)",cases,rejected);
 return true;
}
bool ScriptRunner::exportPersistentState(Common::Array<uint32> &words) const {
 if (!scriptsIdle()) return false;
 exportSettledValues(words); words.push_back(_variantRound); words.push_back(_variantMask);
 return validPersistentState(words);
}
bool ScriptRunner::importPersistentState(const Common::Array<uint32> &words) {
 if (!scriptsIdle() || !validPersistentState(words)) return false;
 Common::Array<uint32> values;
 for (uint i = 0; i < kIdleStateWords; ++i) values.push_back(words[i]);
 importSettledValues(values); _variantRound = words[603]; _variantMask = words[604];
 return true;
}
void ScriptRunner::exportSettledValues(Common::Array<uint32> &words) const {
 words.clear();
 for (int scope = 0; scope < 2; ++scope) for (int i = 0; i < 100; ++i) {
  words.push_back(uint32(_values[scope][i])); words.push_back(uint32(_widths[scope][i])); words.push_back(_known[scope][i]);
 }
 words.push_back(_randomState); words.push_back(_programLoadedAt); words.push_back(_lastTrue);
}
bool ScriptRunner::validIdleState(const Common::Array<uint32> &words) {
 if (words.size() != kIdleStateWords || words[602] > 1) return false;
 for (uint i = 2; i < 600; i += 3) if (words[i] > 1) return false;
 return true;
}
bool ScriptRunner::importIdleState(const Common::Array<uint32> &words) {
 if (!idle() || !validIdleState(words)) return false;
 importSettledValues(words); return true;
}
void ScriptRunner::importSettledValues(const Common::Array<uint32> &words) {
 for (int scope = 0; scope < 2; ++scope) for (int i = 0; i < 100; ++i) {
  const uint n = (scope*100+i)*3;
  _values[scope][i] = int32(words[n]); _widths[scope][i] = int32(words[n+1]); _known[scope][i] = words[n+2] != 0;
 }
 _randomState = words[600]; _programLoadedAt = words[601]; _lastTrue = words[602] != 0;
}
bool ScriptRunner::validVariantState(const Common::Array<uint32> &words) {
 if (words.size() != kIdleStateWords+2) return false;
 Common::Array<uint32> values; for (uint i = 0; i < kIdleStateWords; ++i) values.push_back(words[i]);
 if (!validIdleState(values) || words[603] > 3 || words[604] > 63) return false;
 uint count = 0; for (uint bits = words[604]; bits; bits >>= 1) count += bits & 1;
 return count == words[603];
}
bool ScriptRunner::exportVariantState(Common::Array<uint32> &words) const {
 if (!variantIdle()) return false;
 exportSettledValues(words); words.push_back(_variantRound); words.push_back(_variantMask);
 return validVariantState(words);
}
bool ScriptRunner::importVariantState(const Common::Array<uint32> &words) {
 if (!variantIdle() || !validVariantState(words)) return false;
 importSettledValues(words); _variantRound = words[603]; _variantMask = words[604]; return true;
}
void ScriptRunner::resetGlobals() {
 // _clear_globals 9:408c loops over indices 0..99, storing zero.
 for (int i = 0; i < 100; ++i) defineValue(0, i, 0);
}
bool ScriptRunner::defineValue(int scope, int id, int32 value) {
 if (scope < 0 || scope > 1 || id < 0 || id >= 100) return false;
 _values[scope][id] = value; _known[scope][id] = true; return true;
}
bool ScriptRunner::getValue(int scope, int id, int32 &value) const {
 if (scope < 0 || scope > 1 || id < 0 || id >= 100 || !_known[scope][id]) return false;
 value = _values[scope][id]; return true;
}
void ScriptRunner::loadLocalConditions(const Common::Array<Condition> &conditions) {
 clear();
 _spriteTargets.clear();
 _soundTargets.clear(); _imageTargets.clear(); _movieDurations.clear();
 _gameStateHandler = nullptr;
 _successHandler = nullptr; _soundHandler = nullptr; _successGlobal = _successExtraGlobal = -1;
 _rocketSupport = _eclipseSupport = _planetSupport = _variantSupport = false;
 _orbitHandler = nullptr;
 _rendezvousHandler = nullptr; _probeHandler = nullptr; _ballHandler = nullptr; _cometHandler = nullptr;
 _weatherSupport = _nativePaletteSupport = _worldMovieSupport = _helpSupport = _legacyResumeSupport = false;
 _jupiterSupport = _plotSupport = _dangerSupport = _mentorSupport = _adviceSupport = false;
 _photonSupport = false; _resumeSupport = _resumeFromHelp = false;
 _zodiacSupport = false;
 _noopSuccess = false;
 _programs.clear();
 _clicksBlocked = false; // _do_place 9:01e0 resets the global input lock.
 memset(_known[1], 0, sizeof(_known[1]));
 memset(_widths[1], 0, sizeof(_widths[1]));
 // _load_place 9:2beb-2c39 loads the FOURTH serialized field as value.
 // Scope 0 records update metadata, not global values; do not seed them here.
 for (uint i = 0; i < conditions.size(); ++i) {
  const Condition &c = conditions[i];
  if (c.raw[0] >= 0 && c.raw[0] <= 1 && c.raw[1] >= 0 && c.raw[1] < 100)
   _widths[c.raw[0]][c.raw[1]] = c.raw[2];
  if (c.raw[0] == 1) defineValue(1, c.raw[1], c.raw[3]);
 }
}
bool ScriptRunner::ready(const Script &root, bool allowTimed) const {
 // Validate the entire reachable graph, including cycles, before any effect.
 Common::Array<const Script *> work;
 Common::Array<bool> visited; visited.resize(_programs.size());
 for (uint i = 0; i < visited.size(); ++i) visited[i] = false;
 work.push_back(&root);
 for (uint w = 0; w < work.size(); ++w) {
 const Script &script = *work[w];
 if (!supports(script, allowTimed)) return false;
 for (uint i = 0; i < script.size(); ++i) {
  const Command &c = script[i];
  if (c.opcode == 3 || c.opcode == 4 || c.opcode == 36 || c.opcode == 37) {
   if (uint(c.args[0]) >= _movieDurations.size() || !_movieDurations[c.args[0]]) return false;
   if (c.opcode == 37 && uint64(c.args[1])+uint64(c.args[2]) > _movieDurations[c.args[0]]) return false;
   if (c.opcode == 36 && uint64(c.args[1]) >= _movieDurations[c.args[0]]) return false;
  }
  if (c.opcode == 50 && (!_nativePaletteSupport || !c.text.equalsIgnoreCase("OPEN2_B"))) return false;
  if (c.opcode == 20) {
   Common::String name = c.text; name.toUppercase(); bool found = false;
   for (uint t = 0; t < _imageTargets.size(); ++t) if (_imageTargets[t] == name) found = true;
   if (!found) return false;
  }
  if (c.opcode == 35 && !_resumeSupport && !_dangerSupport && !_worldMovieSupport) return false;
  if (c.opcode == 23) {
   if (c.args[0] == 33) { if (!_legacyResumeSupport) return false; }
    else if (c.args[0] == 22) { if (!_helpSupport) return false; }
   else if (c.args[0] == 29) { if (!_worldMovieSupport) return false; }
   else if (c.args[0] == 27 || c.args[0] == 32) {
    if (!_adviceSupport || !_gameStateHandler) return false;
    for (int global : {6,8,45,55,56,60}) if (!_known[0][global]) return false;
   }
   else if (c.args[0] == 26) {
    const int global = gameStateGlobal(c.args[1],c.args[4]);
    if (global >= 0) {
     if (c.args[3] ? !_known[1][c.args[2]] : !_known[0][global]) return false;
    } else if (!c.args[3] && c.args[1] != 4 && !_gameStateHandler) return false;
   }
   else if (c.args[0] == 21) { if (!_mentorSupport) return false; }
   else if (c.args[0] == 1 || c.args[0] == 4 || c.args[0] == 5 || c.args[0] == 20) {
    if (!_dangerSupport) return false;
   }
   else if (c.args[0] == 23) {
    if (!_plotSupport || !_known[1][4]) return false;
   }
   else if (c.args[0] == 9) {
    if (!_jupiterSupport || !_cometHandler || _soundTargets.size() <= 9 || !_soundTargets[9]) return false;
    for (int local = 0; local < 3; ++local) if (!_known[1][local]) return false;
   }
   else if (c.args[0] == 8) {
    if (!_cometHandler || _soundTargets.size() <= 3 || !_soundTargets[2] || !_soundTargets[3]) return false;
    for (int local = 0; local < 4; ++local) if (!_known[1][local]) return false;
   }
   else if (c.args[0] == 7) {
    if (!_ballHandler || _soundTargets.size() <= 12 || !_soundTargets[6] || !_soundTargets[8] || !_soundTargets[11] || !_soundTargets[12]) return false;
    for (int local = 0; local < 5; ++local) if (!_known[1][local]) return false;
   }
   else if (c.args[0] == 28) {
    if (!_resumeSupport) return false;
    for (int local = 0; local < 6; ++local) if (!_known[1][local]) return false;
    for (int global = 10; global < 20; ++global) if (!_known[0][global]) return false;
   }
   else if (c.args[0] == 11) {
    if (!_zodiacSupport || !_known[1][0] || _soundTargets.size() <= 6 || !_soundTargets[6]) return false;
   }
   else if (c.args[0] == 10) {
    if (!_photonSupport || _soundTargets.size() <= 11 || !_soundTargets[10] || !_soundTargets[11]) return false;
    for (int local = 0; local < 6; ++local) if (!_known[1][local]) return false;
   }
   else if (c.args[0] == 15) {
    if (!_probeHandler || !_known[1][0] || !_known[1][1]) return false;
   }
   else if (c.args[0] == 16) {
    if (!_rendezvousHandler) return false;
    for (int local = 0; local < 8; ++local) if (!_known[1][local]) return false;
   }
   else if (c.args[0] == 24) {
    if (!_weatherSupport || !_soundHandler) return false;
    for (int local = 0; local < 6; ++local) if (!_known[1][local]) return false;
    if (_soundTargets.size() <= 12 || !_soundTargets[10] || !_soundTargets[11] || !_soundTargets[12]) return false;
   }
   else if (c.args[0] == 17) {
    if (!_variantSupport || !_successHandler || !_soundHandler || !_known[0][23]) return false;
   }
   else if (c.args[0] == 13) {
    if (!_orbitHandler) return false;
    for (int local = 0; local < 7; ++local) if (!_known[1][local]) return false;
   }
   else if (c.args[0] == 12) {
    if (!_planetSupport || _soundTargets.size() <= 10 || !_soundTargets[9] || !_soundTargets[10]) return false;
    for (int local = 0; local < 4; ++local) if (!_known[1][local]) return false;
   }
   else if (c.args[0] == 14) { if (!_rocketSupport || !_known[1][0]) return false; }
   else if (c.args[0] == 18) {
    if (!_eclipseSupport) return false;
    for (int local = 0; local < 5; ++local) if (!_known[1][local]) return false;
    if (c.args[1] == 1 && (_soundTargets.size() <= 10 || !_soundTargets[8] || !_soundTargets[9] || !_soundTargets[10])) return false;
   }
   else if (!_rocketSupport && !_noopSuccess && (!_successHandler || _successGlobal < 0 || !_known[0][_successGlobal])) return false;
   if (_successExtraGlobal >= 0 && !_known[0][_successExtraGlobal]) return false;
  }
  if (c.opcode == 39) {
   int32 v;
   if (!getValue(c.args[0],c.args[1],v) || !getValue(c.args[2],c.args[3],v) || _widths[c.args[0]][c.args[1]] < 1 || _widths[c.args[0]][c.args[1]] > 31) return false;
  }
  if (c.opcode == 9 || c.opcode == 27) {
   // _read_command_mem 9:30b0-30d8 decrements the serialized sound id.
   const uint fileId = uint(c.args[0] - 1);
   if (fileId >= _soundTargets.size() || !_soundTargets[fileId]) return false;
  }
  if (c.opcode == 41) {
   const uint target = uint(c.args[0]);
   if (target >= _programs.size() || _programs[target].empty()) return false;
   if (!visited[target]) { visited[target] = true; work.push_back(&_programs[target]); }
  }
  if (c.opcode == 7 || c.opcode == 47 || c.opcode == 48 || c.opcode == 15 || c.opcode == 16 || c.opcode == 17 || c.opcode == 18 || c.opcode == 19 || c.opcode == 24 || c.opcode == 30) {
   if (uint(c.args[0]) > _spriteTargets.size() || !_spriteTargets[c.args[0] - 1]) return false;
   // SWSetCurrentFrameIndex ignores nonnegative indices beyond the end.
   // P515/P536 intentionally request frame1 on the one-frame exhaust.
   if (c.opcode == 24 && uint(c.args[3]) >= _spriteTargets[c.args[0] - 1]) return false;
    if (c.opcode == 48) {
     const int64 first = c.args[1] < 0 ? 0 : c.args[1];
     const int64 maximum = _spriteTargets[c.args[0] - 1] - 1;
     const int64 last = c.args[2] > maximum ? maximum : c.args[2];
     if (first > last || first > 32767 || last > 32767) return false;
    }
  }
  if (c.opcode == 31 || c.opcode == 32 || c.opcode == 33 || c.opcode == 40 || c.opcode == 46) {
   int32 value;
   if (!getValue(c.args[0], c.args[1], value)) return false;
  }
 }
 }
 return true;
}
bool ScriptRunner::supports(const Script &script, bool allowTimed) {
 if (script.empty()) return false;
 int lastCondition = -1;
 for (uint i = 0; i < script.size(); ++i) {
  const Command &c = script[i];
  if (c.delay < -1 || (!allowTimed && c.delay > 0)) return false;
  switch (c.opcode) {
  case 1: case 2: if (!c.args.empty()) return false; break;
  case 5:
   if (c.args.size() != 1 || c.args[0] < 0 || c.args[0] > 537) return false;
   break;
  case 51:
   if (!c.args.empty()) return false;
   break;
  case 6:
   if (!c.args.empty()) return false;
   // Original quit sets the exit flag (15:03b2); P0 closes its condition
   // after that command. Allow those closures, but no following effects.
   for (uint tail = i+1; tail < script.size(); ++tail) if (script[tail].opcode != 42) return false;
   break;
  case 3:
   if (c.args.size() != 4 || c.args[0] < 0 || c.args[0] >= 100 || c.args[1] < 0 || c.args[1] > 640 || c.args[2] < 0 || c.args[2] > 480 || c.args[3] != 0) return false;
   break;
  case 4:
   if (c.args.size() != 1 || c.args[0] < 0 || c.args[0] >= 100) return false;
   break;
  case 37:
   if (c.args.size() != 3 || c.args[0] < 0 || c.args[0] >= 100 || c.args[1] < 0 || c.args[2] <= 0) return false;
   break;
  case 36:
   if (c.args.size() != 2 || c.args[0] < 0 || c.args[0] >= 100 || c.args[1] < 0) return false;
   break;
  case 50:
   if (!c.args.empty() || c.text.empty()) return false;
   break;
  case 20:
   if (c.args.size() != 2 || c.text.empty()) return false;
   break;
  case 35:
  case 49:
   if (!c.args.empty()) return false;
   break;
  case 23:
   if (c.args.size() == 6 && c.args[0] == 33) {
    for (uint a = 1; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 22) {
    if (c.args[1] != 1) return false;
    for (uint a = 2; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 29) {
    for (uint a = 1; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   if (c.args.size() == 6 && (c.args[0] == 27 || c.args[0] == 32)) {
    for (uint a = 1; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 26) {
    if (c.args[1] < 1 || c.args[1] > 14 || c.args[2] < 0 || c.args[2] >= 100 ||
        c.args[3] < 0 || c.args[3] > 1 || c.args[5]) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 21) {
    if (c.args[1] < 1 || c.args[1] > 5) return false;
    for (uint a = 2; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   if (c.args.size() == 6 && (c.args[0] == 1 || c.args[0] == 4 || c.args[0] == 5 || c.args[0] == 20)) {
    if (c.args[0] == 1 ? c.args[1] < 1 || c.args[1] > 6 : c.args[0] == 4 ? c.args[1] < 0 || c.args[1] > 1 : c.args[1] != 0) return false;
    for (uint a = 2; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 23) {
    if (c.args[1] < 1 || c.args[1] > 3) return false;
    for (uint a = 2; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   // Admit the original common success operation; scene support is
   // supplied by the engine, never inferred from the command alone.
   if (c.args.size() == 6 && (c.args[0] == 8 || c.args[0] == 9)) {
    if (c.args[1] < 0 || c.args[1] > 1) return false;
    for (uint a = 2; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 7) {
    if (c.args[1] < 0 || c.args[1] > 4) return false;
    for (uint a = 2; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 28) {
    if (c.args[1] < 0 || c.args[1] > 1) return false;
    for (uint a = 2; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 11) {
    for (uint a = 1; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 10) {
    if (c.args[1] < 0 || c.args[1] > 1) return false;
    for (uint a = 2; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 15) {
    if (c.args[5]) return false;
    if (c.args[1] == 0) {
     if (c.args[2] < 15 || c.args[2] > 17) return false;
     if (c.args[3] != (c.args[2] == 16 ? 106 : 0) || c.args[4] != (c.args[2] == 16 ? 53 : 0)) return false;
    } else if (c.args[1] != 1 || c.args[2] || c.args[3] || c.args[4]) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 16) {
    if (c.args[1] < 0 || c.args[1] > 3) return false;
    for (uint a = 2; a < 6; ++a) if (c.args[a]) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 24) {
    if (c.args[1] < 0 || c.args[1] > 3 || c.args[4] || c.args[5]) return false;
    if (c.args[2] != (c.args[1] ? 160 : 0) || c.args[3] != (c.args[1] ? 57 : 0)) return false;
    break;
   }
   if (c.args.size() == 6 && c.args[0] == 13) {
    if (c.args[5] != 0) return false;
    if (c.args[1] == 0) {
     if (c.args[2] != 20 && c.args[2] != 22 && c.args[2] != 23) return false;
     if (c.args[3] != (c.args[2] == 23 ? 13 : 0) || c.args[4] != (c.args[2] == 23 ? -50 : 0)) return false;
    } else if (c.args[1] != 1 || c.args[2] || c.args[3] || c.args[4]) return false;
    break;
   }
   if (c.args.size() != 6 || (c.args[0] != 25 && c.args[0] != 14 && c.args[0] != 18 && c.args[0] != 12 && c.args[0] != 17)) return false;
   if ((c.args[0] == 18 || c.args[0] == 12) && (c.args[1] < 0 || c.args[1] > 1)) return false;
   for (uint a = (c.args[0] == 18 || c.args[0] == 12) ? 2 : 1; a < 6; ++a) if (c.args[a] != 0) return false;
   break;
  case 21: case 25: case 26:
   if (!c.args.empty()) return false;
   break;
  case 10:
   if (c.args.size() != 1) return false;
   break;
  case 9: case 27:
   if (c.args.size() != 1 || c.args[0] < 1 || c.args[0] > 923) return false;
   break;
  case 28: case 29:
   if (c.args.size() != 1 || c.args[0] >= 0) return false;
   break;
  case 41:
   if (c.args.size() != 1 || c.args[0] < 0 || c.args[0] > 32767) return false;
   break;
  case 16: case 17: case 30:
   if (c.args.size() != 1 || c.args[0] <= 0) return false;
   break;
  case 19:
   // 15:0827-08b8 stores frame parameters and sets the signed-word timer.
   // Only the ordinary forward cycle is currently reconstructed.
   if (c.args.size() != 4 || c.args[0] <= 0 || c.args[1] < -1 || c.args[1] > 32767 || (c.args[2] != 1 && !(c.args[1] == -1 && c.args[2] == 0)) || c.args[3] != 0) return false;
   break;
  case 18:
   // 15:08bb-0a91. Admit reconstructed bounce/wrap callbacks only.
   if (c.args.size() != 6 || c.args[0] <= 0 || c.args[1] < -1 || c.args[1] > 32767 || c.args[2] < -32768 || c.args[2] > 32767 || c.args[3] < -32768 || c.args[3] > 32767 || c.args[4] < 1 || c.args[4] > 2 || c.args[5] != 0) return false;
   break;
  case 24:
   if (c.args.size() != 4 || c.args[0] <= 0 || c.args[3] < 0 || c.args[3] > 32767) return false;
   break;
  case 7: case 47: case 48:
   if (c.args.size() != 3 || c.args[0] <= 0) return false;
   break;
  case 15:
   if (c.args.size() != 2 || c.args[0] <= 0 || c.args[1] < 0 || c.args[1] > 32767) return false;
   break;
  case 39:
   if (c.args.size() != 4 || c.args[0] < 0 || c.args[0] > 1 || c.args[2] < 0 || c.args[2] > 1 || c.args[1] < 0 || c.args[1] >= 100 || c.args[3] < 0 || c.args[3] >= 100) return false;
   break;
  case 40:
   // Original bounds and width are signed 16-bit. Admit the non-wrapping,
   // nonnegative subset; the result is zero-extended by the handler.
   if (c.args.size() != 4 || c.args[0] < 0 || c.args[0] > 1 || c.args[1] < 0 || c.args[1] >= 100 || c.args[2] < 0 || c.args[3] > 32767 || c.args[3] < c.args[2] || c.args[3] - c.args[2] >= 32767) return false;
   break;
  case 33:
   if (c.args.size() != 4 || c.args[0] < 0 || c.args[0] > 1 || c.args[1] < 0 || c.args[1] >= 100 || c.args[2] < 0 || c.args[2] > 30 || (c.args[3] != 0 && c.args[3] != 1)) return false;
   break;
  case 31: case 32: case 46:
   if (c.args.size() != (c.opcode == 31 ? 6U : 3U)) return false;
   if (c.args[0] < 0 || c.args[0] > 1 || c.args[1] < 0 || c.args[1] >= 100) return false;
   if (c.opcode == 31) {
    if (c.args[4] < 0 || c.args[4] > 3) return false;
    lastCondition = i;
   }
   break;
  case 42: case 45:
   if (!c.args.empty() || lastCondition < 0) return false;
   break;
  default: return false;
  }
 }
 // Follow only continuations that can execute before the scene reload.
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
 for (uint root = 0; root < script.size(); ++root) if (script[root].opcode == 5 || script[root].opcode == 51) {
  Common::Array<int> work; work.push_back(root+1);
  Common::Array<bool> seen; seen.resize(script.size());
  for (uint i = 0; i < seen.size(); ++i) seen[i] = false;
  for (uint w = 0; w < work.size(); ++w) {
   const int index = work[w];
   if (index < 0 || uint(index) >= script.size() || seen[index] || script[index].delay != -1) continue;
   seen[index] = true;
   const int opcode = script[index].opcode;
   // State-only commands execute on the old scene before actions are applied.
   // Template calls merely enqueue work, which scene reload discards.
   // Displaying an already staged image (49) still uses the old scene.
   // 15:0385 only requests a reload; the engine drains actions before it.
   // Other visual/audio effects still need unimplemented transition context.
   if (opcode != 1 && opcode != 2 && opcode != 31 && opcode != 42 && opcode != 45 &&
       opcode != 32 && opcode != 33 && opcode != 39 && opcode != 40 && opcode != 46 && opcode != 41 && opcode != 49) return false;
   work.push_back(index+1);
   if (opcode == 31) work.push_back(links[index]);
   if (opcode == 45 && uint(index+1) < script.size()) work.push_back(links[index+1]);
  }
 }
 return true;
}
bool ScriptRunner::start(const Script &script, uint32 now, bool allowTimed) {
 // Preflight the whole chain: unsupported scripts have no partial effects.
 if (!supports(script, allowTimed) || !ready(script, allowTimed)) return false;
 execute(script, 0, now);
 return true;
}
bool ScriptRunner::enqueue(const Script &script, uint32 now, bool allowTimed) {
 if (!supports(script, allowTimed) || !ready(script, allowTimed)) return false;
 Pending p; p.script = script; p.index = 0; p.since = now;
 _pending.push_back(p);
 return true;
}
uint ScriptRunner::enqueueStartup(const Common::Array<Script> &scripts, uint32 now, bool allowTimed) {
 // _load_place 9:2796 enqueues each entry script in serialized order.
 // A partially supported chain is rejected as a whole. The caller reports
 // skipped chains: this experimental subset is not complete scene behavior.
 uint accepted = 0;
 for (uint i = 0; i < scripts.size(); ++i)
  if (!scripts[i].empty() && enqueue(scripts[i], _programLoadedAt, allowTimed)) ++accepted;
 return accepted;
}
void ScriptRunner::execute(const Script &script, uint index, uint32 now) {
 // Reproduce the reader's single last-condition pointer, not a nesting stack.
 Common::Array<int> links; links.resize(script.size());
 int last = -1;
 for (uint i = 0; i < script.size(); ++i) {
  links[i] = -1;
  if (script[i].opcode == 31) last = i;
  if (last >= 0 && i + 1 < script.size()) {
   if (script[i].opcode == 45) links[last] = i;
   if (script[i].opcode == 42) links[last] = i + 1;
  }
 }
 while (index < script.size()) {
  const Command &c = script[index];
  ++_executed;
  bool result = true, skipElse = false;
  const bool blockingSound = c.opcode == 9 && _soundHandler && _soundHandler->isBlockingSound(c.args[0]-1);
  if (blockingSound) now = _soundHandler->onBlockingSound(c.args[0]-1, now);
  if (c.opcode == 23) {
   if (c.args[0] == 33) {
    Action resume = {23,33,0,0}; _actions.push_back(resume);
   } else if (c.args[0] == 22) {
    Action help = {23,22,0,0}; _actions.push_back(help);
   } else if (c.args[0] == 29) {
    Action redraw = {23,29,0,0}; _actions.push_back(redraw);
   } else if (c.args[0] == 27) {
    const AdviceResult advice = chooseAdvice(_mentorPrevious,_gameStateHandler->gameStateContext().completed,
     _values[0][45],_values[0][6],_values[0][55],_values[0][56],
     [&](int low,int high) { return low+uint32(random15())*(high-low+1)/32768; });
    defineValue(1,0,advice.side); defineValue(0,6,advice.stage);
    defineValue(0,55,advice.flag55); defineValue(0,56,advice.flag56);
    Action range = {37,0,advice.clip.start,advice.clip.duration}; _actions.push_back(range);
    Action stop = {4,0,0,0}; _actions.push_back(stop);
   } else if (c.args[0] == 32) {
    if (adviceStartsClock(_values[0][45],uint32(_values[0][8]))) {
     defineValue(0,60,1); defineValue(0,8,int32(now));
    }
   } else if (c.args[0] == 26) {
    const int key = c.args[1], local = c.args[2], global = gameStateGlobal(key,c.args[4]);
    if (global >= 0) {
     if (c.args[3]) defineValue(0,global,_values[1][local]);
     else defineValue(1,local,_values[0][global]);
    } else if (!c.args[3] && key != 4) {
     defineValue(1,local,gameStateExternalValue(key,_gameStateHandler->gameStateContext()));
    }
   } else if (c.args[0] == 21) {
    const MentorClip clip = mentorClip(c.args[1],_mentorPrevious,_known[0][10] ? _values[0][10] : 0);
    defineValue(1,0,clip.duration ? 0 : 1);
    if (clip.duration) {
     Action range = {37,0,clip.start,clip.duration}; _actions.push_back(range);
     Action stop = {4,0,0,0}; _actions.push_back(stop);
    }
   } else if (c.args[0] == 28) {
    for (int local = 0; local < 10; ++local) {
     if (c.args[1] == 0) defineValue(0,local+10,_known[1][local] ? _values[1][local] : 0);
     else if (_resumeFromHelp) defineValue(1,local,_values[0][local+10]);
    }
   } else if (c.args[0] == 11) {
    if (_zodiacRegion >= 1 && _zodiacRegion <= 12) {
     Action sound = {9,6,0,0}; _actions.push_back(sound);
     Action show = {16,17+_zodiacRegion,0,0}; _actions.push_back(show);
     _values[1][0] = _zodiacRegion;
    }
   } else if (c.args[0] == 10) {
    if (c.args[1] == 0) {
     Action photon = {23,10,_values[1][0],0}; _actions.push_back(photon);
    } else {
     const int sound = photonAnswer(_values[1][0],_values[1][1]);
     _values[1][3] = sound == -1;
     if (sound >= 0) { Action response = {9,sound,0,0}; _actions.push_back(response); }
    }
   } else if (c.args[0] == 1 || c.args[0] == 4 || c.args[0] == 5 || c.args[0] == 20) {
    Action danger = {23,c.args[0],c.args[1],0}; _actions.push_back(danger);
   } else if (c.args[0] == 23) {
    Action plot = {23,23,c.args[1],0}; _actions.push_back(plot);
   } else if (c.args[0] == 8 || c.args[0] == 9) {
    _cometHandler->onComet(c.args[1],now);
   } else if (c.args[0] == 7) {
    _ballHandler->onBall(c.args[1],now);
   } else if (c.args[0] == 15) {
    _probeHandler->onProbe(c.args[1],c.args[2]);
    if (c.args[1] == 1 || c.args[2] == 17) _values[1][1] = c.args[1];
   } else if (c.args[0] == 16) {
    if (_rendezvousHandler->onRendezvous(c.args[1],_values[1][5],now) && c.args[1] == 3) {
     cancelPending(); _values[1][6] = 1;
    }
   } else if (c.args[0] == 24) {
    if (c.args[1] == 0) {
     const int sound = weatherAnswer(_values[1][4],_values[1][0],_values[1][1],_values[1][2]);
     if (sound != -2) _values[1][5] = sound == -1;
     if (sound >= 0) {
      if (_soundHandler->isBlockingSound(sound)) now = _soundHandler->onBlockingSound(sound,now);
      else { Action response = {9,sound,0,0}; _actions.push_back(response); }
     }
    } else {
     Action movie = {23,24,c.args[1],0}; _actions.push_back(movie);
    }
   } else if (c.args[0] == 17) {
    if (_variantRound == 3) {
     _variantRound = _variantMask = 0;
     if (!_values[0][23]) now = _successHandler->onPuzzleSuccess(now);
     _values[0][23] = 1;
     now = _soundHandler->onBlockingSound(922,now);
     Command go; go.opcode = 5; go.args.push_back(519); go.delay = 3000;
     Pending exit; exit.script.push_back(go); exit.index = 0; exit.since = now;
     _pending.push_back(exit);
    } else {
     uint rank = 1 + uint32(random15())*(6-_variantRound)/32768;
     for (uint bit = 0; bit < 6; ++bit) {
      if (_variantMask & (1U << bit)) continue;
      if (--rank) continue;
      _variantMask |= 1U << bit; ++_variantRound;
      Action next = {5,bit == 0 ? 506 : int32(530+bit),0,0}; _actions.push_back(next);
      break;
     }
    }
   } else if (c.args[0] == 13) {
    if (c.args[1] == 0) {
     Action orbit = {23,13,c.args[2],c.args[3]}; orbit.motion[0] = c.args[4]; _actions.push_back(orbit);
    } else {
     // The following condition observes local4 in this same script pass.
     _values[1][4] = _orbitHandler->onOrbitAnswer(_values[1][2],_values[1][3],now);
    }
   } else if (c.args[0] == 12) {
    const int32 setting = _values[1][0], planet = _values[1][2];
    if (c.args[1] == 0 || setting > 0) {
     Action launch = {23,12,c.args[1],planet}; launch.motion[0] = setting; _actions.push_back(launch);
     if (c.args[1] == 1 && (setting+planet == 10 || setting-planet == 9)) ++_values[1][3];
    }
   } else if (c.args[0] == 14) {
    Action launch = {23,14,0,0}; _actions.push_back(launch);
   } else if (c.args[0] == 18) {
    const int32 phase = _values[1][0], quadrant = _values[1][1];
    if (c.args[1] == 0) {
     Action move = {23,18,phase,quadrant}; _actions.push_back(move);
    } else {
     int sound = 10;
     if ((phase == 0 && quadrant == 1) || (phase == 6 && quadrant == 3)) { _values[1][3] = 1; sound = 8; }
     else if ((phase == 0 && quadrant == 3) || (phase == 6 && quadrant == 1)) { _values[1][4] = 1; sound = 9; }
     _values[1][2] = _values[1][3] == 1 && _values[1][4] == 1;
     // Direct _playSound IDs in 4:448e/44da/44de, no reader decrement.
     Action response = {9,sound,0,0}; _actions.push_back(response);
    }
   } else if (!_rocketSupport && !_noopSuccess) {
   // Original per-scene dispatch uses a DWORD within the global array.
   // Sound and counter happen before the flag store, only when it was zero.
   if (_values[0][_successGlobal] == 0) now = _successHandler->onPuzzleSuccess(now);
   _values[0][_successGlobal] = 1;
   // P529 additionally unlocks global60 on every invocation (4:5a54).
   if (_successExtraGlobal >= 0) _values[0][_successExtraGlobal] = 1;
   } // P537 has no case in the original command-25 dispatch table.
  } else if (c.opcode == 31) {
   const int32 v = _values[c.args[0]][c.args[1]];
   switch (c.args[4]) {
   case 0: result = v == c.args[2]; break;
   case 1: result = v < c.args[2]; break;
   case 2: result = v > c.args[2]; break;
   case 3: result = v >= c.args[2] && v <= c.args[3]; break;
   }
   _lastTrue = result;
  } else if (c.opcode == 32) {
   _values[c.args[0]][c.args[1]] = c.args[2];
  } else if (c.opcode == 39) {
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
  } else if (c.opcode == 40) {
   const uint32 width = uint32(c.args[3] - c.args[2] + 1);
   _values[c.args[0]][c.args[1]] = c.args[2] + (uint32(random15()) * width) / 32768;
  } else if (c.opcode == 33) {
   // Original uses pow(2, bit), then OR for set, or TEST + SUB for clear.
   // For admitted bits 0..30 this is exact and has no floating conversion.
   const uint32 mask = uint32(1) << c.args[2];
   uint32 value = uint32(_values[c.args[0]][c.args[1]]);
   if (c.args[3] == 1) value |= mask;
   else if (value & mask) value -= mask;
   _values[c.args[0]][c.args[1]] = int32(value);
  } else if (c.opcode == 46) {
   int32 &v = _values[c.args[0]][c.args[1]];
   // Original x86 ADD wraps modulo 2^32; avoid signed overflow in C++.
   v = int32(uint32(v) + uint32(c.args[2]));
  } else if (c.opcode == 28 || c.opcode == 29) {
   _clicksBlocked = c.opcode == 28;
  } else if (c.opcode == 41) {
   // 15:118b indexes the zero-based command table and calls _pend_command.
   // Appending, rather than executing recursively, preserves queue ordering.
   // _copy_command 15:1ad4 copies the timestamp initialized at 9:340f.
   // Calling a template does not restart its first-command timer.
   Pending p; p.script = _programs[c.args[0]]; p.index = 0; p.since = _programLoadedAt;
   _pending.push_back(p);
  } else if (c.opcode == 42) {
   _lastTrue = true;
  } else if (c.opcode == 45) {
   skipElse = _lastTrue;
  }
  if (c.opcode == 3 || c.opcode == 37) {
   Action movie = {c.opcode, c.args[0], c.args[1], c.args[2]}; _actions.push_back(movie);
  }
  if (c.opcode == 19) {
   Action frames = {19,c.args[0],c.args[1],c.args[2]}; _actions.push_back(frames);
  }
  if (c.opcode == 4) { Action stop = {4,c.args[0],0,0}; _actions.push_back(stop); }
  if (c.opcode == 36) { Action seek = {36,c.args[0],c.args[1],0}; _actions.push_back(seek); }
  if (c.opcode == 18) {
   Action movement = {18,c.args[0],c.args[1],c.args[2]};
   movement.motion[0] = c.args[3]; movement.motion[1] = c.args[4]; movement.motion[2] = c.args[5];
   _actions.push_back(movement);
  }
  if (c.opcode == 21) { Action flash = {21,0,0,0}; _actions.push_back(flash); }
  if (c.opcode == 24) {
   // 15:0a94-0b2a: absolute move (including stored x/y), then frame.
   // Both actions are consumed before the engine redraws the sprite world.
   Action move = {7,c.args[0],c.args[1],c.args[2]}; _actions.push_back(move);
   Action frame = {15,c.args[0],c.args[3],0}; _actions.push_back(frame);
  }
  if (c.opcode == 50) { Action palette = {50,0,0,0,c.text}; _actions.push_back(palette); }
  if (c.opcode == 20) {
   Action image = {20, 0, int16(c.args[0]), int16(c.args[1]), c.text};
   _actions.push_back(image);
  }
  if (c.opcode == 35 || c.opcode == 49 || c.opcode == 25 || c.opcode == 26 || c.opcode == 27 || c.opcode == 10 || (c.opcode == 9 && !blockingSound) || c.opcode == 5 || c.opcode == 6 || c.opcode == 51 || c.opcode == 7 || c.opcode == 47 || c.opcode == 48 || c.opcode == 15 || c.opcode == 16 || c.opcode == 17 || c.opcode == 30) {
   Action action = { c.opcode, c.opcode == 27 || c.opcode == 9 || c.opcode == 5 || c.opcode == 7 || c.opcode == 47 || c.opcode == 48 || c.opcode == 15 || c.opcode == 16 || c.opcode == 17 || c.opcode == 30 ? c.args[0] : 0, 0, 0 };
   if (c.opcode == 9 || c.opcode == 27) --action.value;
   if (c.opcode == 15) action.x = c.args[1];
   if (c.opcode == 7 || c.opcode == 47 || c.opcode == 48) { action.x = c.args[1]; action.y = c.args[2]; }
   _actions.push_back(action);
  }
  int next = index + 1;
  if (uint(next) >= script.size()) return;
  if (!result) next = links[index];
  else if (skipElse) next = links[next];
  if (next < 0 || uint(next) >= script.size()) return;
  index = next;
  if (script[index].delay != -1) {
   Pending p; p.script = script; p.index = index; p.since = now;
   _pending.push_back(p);
   return;
  }
 }
}
void ScriptRunner::tick(uint32 now) {
 // _handle_pending snapshots the queue count. A newly queued zero-delay
 // continuation must wait for another pass, even if it is already due.
 const uint count = _pending.size();
 const uint epoch = _pendingEpoch;
 uint index = 0;
 for (uint i = 0; i < count; ++i) {
  const Pending p = _pending[index];
  const int32 delay = p.script[p.index].delay;
  if (_programs.size() == 11 && _programs[0].size() == 7 && p.script[p.index].opcode == 41 && p.script[p.index].args.size() == 1 && !p.script[p.index].args[0] && delay == 200)
   debug("Probe audit poll: %u %u %d %u %u %u",now,p.since,delay,uint(int32(now-p.since) >= delay),count,p.index);

  if (delay == 0 || int32(now - p.since) >= delay) {
   _pending.remove_at(index);
   execute(p.script, p.index, now);
   if (epoch != _pendingEpoch) break;
  } else {
   ++index;
  }
 }
}
bool ScriptRunner::popAction(Action &action) {
 if (_actions.empty()) return false;
 action = _actions[0]; _actions.remove_at(0); return true;
}

// Exercises scheduler behavior derived from ASTRO.EXE segment 15, including
// deferred zero delay, immediate -1, timer wraparound and atomic rejection.
bool verifyScriptRunner() {
 ScriptRunner vm; ScriptRunner::Action action; Script s;
 Command nop; nop.opcode = 1; nop.delay = 0;
 Command go; go.opcode = 5; go.args.push_back(126); go.delay = 0;
 s.push_back(nop); s.push_back(nop); s.push_back(go);
 if (!vm.start(s, 100) || vm.pendingCount() != 1 || vm.popAction(action)) return false;
 vm.tick(100);
 if (vm.pendingCount() != 1 || vm.popAction(action)) return false;
 vm.tick(100);
 if (!vm.popAction(action) || action.opcode != 5 || action.value != 126 || vm.pendingCount()) return false;
 s[1].delay = s[2].delay = -1;
 if (!vm.start(s, 100) || !vm.popAction(action) || vm.pendingCount()) return false;
 s[1].delay = 5;
 if (vm.start(s, 0)) return false;
 if (!vm.start(s, 0xfffffffdU, true)) return false;
 vm.tick(1);
 if (vm.popAction(action)) return false;
 vm.tick(2);
 if (!vm.popAction(action) || vm.pendingCount()) return false;
 s[1].opcode = 31;
 if (vm.start(s, 100, true) || vm.pendingCount() || vm.popAction(action)) return false;
 s[1] = nop;
 if (!vm.start(s, 100)) return false;
 vm.clear(); vm.tick(100);
 if (vm.pendingCount() || vm.popAction(action)) return false;
 // _do_command executes the first command immediately; only successors
 // are delayed by _execute_command. Event entry policies are separate.
 Script direct; direct.push_back(go);
 if (!vm.start(direct, 0) || !vm.popAction(action) || action.value != 126) return false;
 if (!vm.enqueue(direct, 0) || vm.popAction(action)) return false;
 vm.tick(0);
 if (!vm.popAction(action) || action.value != 126 || vm.pendingCount()) return false;
 // Existing ready work precedes a newly appended continuation.
 s[1] = nop; s[2].delay = 0;
 direct[0].args[0] = 127;
 if (!vm.enqueue(s, 0) || !vm.enqueue(direct, 0)) return false;
 vm.tick(0);
 if (!vm.popAction(action) || action.value != 127 || vm.popAction(action)) return false;
 vm.tick(0);
 if (vm.popAction(action)) return false;
 vm.tick(0);
 if (!vm.popAction(action) || action.value != 126 || vm.pendingCount()) return false;
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
 // Delayed template heads retain the load epoch on startup and each call.
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
 vm.tick(25000); if (!vm.popAction(action) || vm.pendingCount()) return false;
 // Synchronous sound finishes before the next command's relative timer starts.
 struct BlockingTest : ScriptRunner::SoundHandler {
  uint calls = 0;
  bool isBlockingSound(int id) const override { return id == 2; }
  uint32 onBlockingSound(int id, uint32 now) override { ++calls; return now + 1200; }
 } blockingTest;
 vm.setSoundHandler(&blockingTest);
 Common::Array<bool> blockingTargets; blockingTargets.resize(3); blockingTargets[2] = true;
 vm.setSoundTargets(blockingTargets);
 Script speech; Command speechCommand; speechCommand.opcode = 9; speechCommand.args.push_back(3); speech.push_back(speechCommand);
 Command afterSpeech = go; afterSpeech.delay = 500; speech.push_back(afterSpeech);
 if (!vm.start(speech,100,true) || blockingTest.calls != 1 || vm.popAction(action)) return false;
 vm.tick(1799); if (vm.popAction(action)) return false;
 vm.tick(1800); if (!vm.popAction(action) || action.value != 126 || vm.pendingCount()) return false;
 speech[1].delay = -1;
 if (!vm.start(speech,2000,true) || blockingTest.calls != 2 || !vm.popAction(action) || vm.pendingCount() || vm.popAction(action)) return false;
 vm.setSoundHandler(nullptr);
 Common::Array<bool> sounds; sounds.resize(900);
 for (uint i = 0; i < sounds.size(); ++i) sounds[i] = true;
 vm.setSoundTargets(sounds);
 const int rawIds[] = {1,2,9,900};
 for (uint opcodeIndex = 0; opcodeIndex < 2; ++opcodeIndex) {
  for (uint i = 0; i < ARRAYSIZE(rawIds); ++i) {
   Script soundScript; Command sound; sound.opcode = opcodeIndex ? 27 : 9;
   sound.args.push_back(rawIds[i]); soundScript.push_back(sound);
   if (!vm.start(soundScript,0) || !vm.popAction(action) || action.opcode != sound.opcode || action.value != rawIds[i]-1 || vm.popAction(action)) return false;
   soundScript[0].args[0] = 0; if (vm.start(soundScript,0)) return false;
   soundScript[0].args[0] = 901; if (vm.start(soundScript,0)) return false;
  }
 }
 return true;
}
}


