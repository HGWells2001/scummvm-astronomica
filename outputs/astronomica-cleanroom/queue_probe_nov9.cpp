// SPDX-License-Identifier: GPL-3.0-or-later
// Compare original queue instruction fixtures with the actual ScriptRunner.
#define FORBIDDEN_SYMBOL_ALLOW_ALL
#include <cstdio>
#include <cstdlib>
#include "astronomica/script.h"
static uint32 word(FILE*f){byte b[4];if(fread(b,1,4,f)!=4)exit(2);return uint32(b[0])|(uint32(b[1])<<8)|(uint32(b[2])<<16)|(uint32(b[3])<<24);}
static Astronomica::Script script(FILE*f){
 Astronomica::Script s;uint n=word(f);if(!n||n>1000)exit(2);
 for(uint i=0;i<n;++i){Astronomica::Command c;c.opcode=word(f);c.delay=int32(word(f));uint args=word(f);if(args>6)exit(2);for(uint j=0;j<args;++j)c.args.push_back(int32(word(f)));s.push_back(c);}return s;
}
int main(int argc,char**argv){
 if(argc!=2)return 2;FILE*f=fopen(argv[1],"rb");if(!f)return 2;char magic[8];if(fread(magic,1,8,f)!=8||memcmp(magic,"QSCN0001",8))return 2;
 uint cases=word(f),ticks=0;uint32 aggregate=2166136261U;if(!cases||cases>1000)return 2;
 for(uint row=0;row<cases;++row){
  uint scene=word(f),ordinal=word(f);int32 seed=int32(word(f));uint32 loaded=word(f);uint count=word(f),steps=word(f);if(!count||count>100||!steps||steps>100)return 2;
  Common::Array<Astronomica::Script> programs;for(uint i=0;i<count;++i)programs.push_back(script(f));Astronomica::Script root=script(f);
  Astronomica::ScriptRunner runner;runner.setPrograms(programs,loaded);
  Common::Array<bool> sounds;sounds.resize(11000);for(uint i=0;i<sounds.size();++i)sounds[i]=true;runner.setSoundTargets(sounds);
  for(int scope=0;scope<2;++scope)for(int id=0;id<100;++id)if(!runner.defineValue(scope,id,seed))return 3;
  if(!runner.enqueue(root,loaded,true)){fprintf(stderr,"FAIL queue admission P%u/%u/seed%d\n",scene,ordinal,seed);return 4;}
  for(uint step=0;step<steps;++step){
   uint32 now=word(f),executed=word(f),pending=word(f),expectedActions=word(f),expectedHash=word(f);uint32 values[200];for(uint i=0;i<200;++i)values[i]=word(f);
   runner.tick(now);uint32 hash=2166136261U;uint actions=0;Astronomica::ScriptRunner::Action a;
   while(runner.popAction(a)){if(a.opcode!=9)return 5;hash=(hash^uint32(a.value+1))*16777619U;++actions;}
   if(runner.executedCount()!=executed||runner.pendingCount()!=pending||actions!=expectedActions||hash!=expectedHash){fprintf(stderr,"FAIL queue P%u/%u/seed%d/at%u: executed%u/%u pending%u/%u actions%u/%u hash%08x/%08x\n",scene,ordinal,seed,now,runner.executedCount(),executed,runner.pendingCount(),pending,actions,expectedActions,hash,expectedHash);return 6;}
   for(int scope=0;scope<2;++scope)for(int id=0;id<100;++id){int32 value;if(!runner.getValue(scope,id,value)||uint32(value)!=values[scope*100+id]){fprintf(stderr,"FAIL queue scalar P%u/%u/at%u/scope%d/id%d\n",scene,ordinal,now,scope,id);return 7;}}
   for(uint32 v:{scene,ordinal,uint32(seed),now,executed,pending,actions,hash})aggregate=(aggregate^v)*16777619U;++ticks;
  }
 }
 if(fgetc(f)!=EOF)return 2;fclose(f);printf("Original queue native PASS:cases%u,ticks%u,aggregate%08x\n",cases,ticks,aggregate);return 0;
}
