// SPDX-License-Identifier: GPL-3.0-or-later
// Native control-flow regression using the real ScriptRunner implementation.
// Input is a local reduced-control fixture, not a playable game or prototype.
#define FORBIDDEN_SYMBOL_ALLOW_ALL
#include <cstdio>
#include <cstdlib>
#include "astronomica/script.h"

static uint32 word(FILE *f) {
 byte b[4];if(fread(b,1,4,f)!=4){fprintf(stderr,"Truncated control fixture\n");exit(2);}
 return uint32(b[0])|(uint32(b[1])<<8)|(uint32(b[2])<<16)|(uint32(b[3])<<24);
}
int main(int argc,char **argv) {
 if(argc!=2)return 2;
 FILE *f=fopen(argv[1],"rb");if(!f)return 2;
 char magic[8];if(fread(magic,1,8,f)!=8||memcmp(magic,"CBLK0001",8))return 2;
 const uint scripts=word(f);uint cases=0;uint32 aggregate=2166136261U;
 if(!scripts||scripts>2000)return 2;
 for(uint row=0;row<scripts;++row){
  const uint scene=word(f),ordinal=word(f),length=word(f),count=word(f);
  if(!length||length>1000||!count||count>1000)return 2;
  Astronomica::Script reduced;
  for(uint i=0;i<length;++i){
   Astronomica::Command c;c.opcode=word(f);const uint args=word(f);c.delay=-1;
   if((c.opcode==31&&args!=6)||(c.opcode==9&&args!=1)||((c.opcode==42||c.opcode==45)&&args)||!(c.opcode==31||c.opcode==42||c.opcode==45||c.opcode==9))return 2;
   for(uint n=0;n<args;++n)c.args.push_back(int32(word(f)));
   reduced.push_back(c);
  }
  for(uint sample=0;sample<count;++sample){
   const int32 value=int32(word(f));const uint32 expectedHash=word(f),expectedExecuted=word(f),expectedActions=word(f);
   Astronomica::ScriptRunner runner;
   Common::Array<bool> targets;targets.resize(length+1);for(uint i=0;i<targets.size();++i)targets[i]=true;
   runner.setSoundTargets(targets);
   for(uint scope=0;scope<2;++scope)for(uint id=0;id<100;++id)if(!runner.defineValue(scope,id,value))return 3;
   if(!runner.enqueue(reduced,0,true)){fprintf(stderr,"FAIL admission P%u/script%u/sample%u\n",scene,ordinal,sample);return 4;}
   runner.tick(0);uint32 hash=2166136261U;uint actions=0;
   Astronomica::ScriptRunner::Action action;
   while(runner.popAction(action)){
    if(action.opcode!=9||action.value<0||uint(action.value)>=length)return 5;
    hash=(hash^uint32(action.value+1))*16777619U;++actions;
   }
   if(hash!=expectedHash||runner.executedCount()!=expectedExecuted||actions!=expectedActions||runner.pendingCount()){
    fprintf(stderr,"FAIL native control P%u/script%u/sample%u/value%d: hash%08x/%08x executed%u/%u actions%u/%u pending%u\n",scene,ordinal,sample,value,hash,expectedHash,runner.executedCount(),expectedExecuted,actions,expectedActions,runner.pendingCount());return 6;
   }
   for(uint32 v:{scene,ordinal,uint32(value),hash,expectedExecuted,expectedActions})aggregate=(aggregate^v)*16777619U;
   ++cases;
  }
  printf("Original control native script: PASS (P%u,script%u,commands%u,cases%u)\n",scene,ordinal,length,count);
 }
 if(fgetc(f)!=EOF)return 7;fclose(f);
 printf("Original condition-control native verification: PASS (scripts%u,cases%u,aggregate%08x; real ScriptRunner,reduced effects,no Windows runtime claim)\n",scripts,cases,aggregate);
 return 0;
}
