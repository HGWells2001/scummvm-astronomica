// SPDX-License-Identifier: GPL-3.0-or-later
#define FORBIDDEN_SYMBOL_ALLOW_ALL
#include <cstdio>
#include <cstdlib>
#include "astronomica/script.h"
static uint32 word(FILE*f){byte b[4];if(fread(b,1,4,f)!=4)exit(2);return uint32(b[0])|(uint32(b[1])<<8)|(uint32(b[2])<<16)|(uint32(b[3])<<24);}
int main(int argc,char**argv){
 if(argc!=2)return 2;FILE*f=fopen(argv[1],"rb");if(!f)return 2;char magic[8];if(fread(magic,1,8,f)!=8||memcmp(magic,"TDUE0001",8))return 2;
 const uint cases=word(f);if(!cases||cases>10000)return 2;uint32 aggregate=2166136261U;
 for(uint row=0;row<cases;++row){
  const int32 delay=int32(word(f));const uint32 since=word(f),now=word(f),due=word(f);
  Astronomica::ScriptRunner runner;Common::Array<bool>targets;targets.push_back(true);runner.setSoundTargets(targets);
  Astronomica::Script script;Astronomica::Command c;c.opcode=9;c.args.push_back(1);c.delay=delay;script.push_back(c);
  if(!runner.enqueue(script,since,true))return 3;runner.tick(now);Astronomica::ScriptRunner::Action action;uint actions=0;while(runner.popAction(action)){if(action.opcode!=9||action.value)return 4;++actions;}
  if(actions!=due||runner.executedCount()!=due||runner.pendingCount()!=1-due){fprintf(stderr,"FAIL delay row%u delay%d since%u now%u expected%u actual%u\n",row,delay,since,now,due,actions);return 5;}
  for(uint32 v:{uint32(delay),since,now,due})aggregate=(aggregate^v)*16777619U;
 }
 if(fgetc(f)!=EOF)return 6;fclose(f);
 {Astronomica::ScriptRunner runner;Common::Array<bool>targets;targets.push_back(true);targets.push_back(true);runner.setSoundTargets(targets);Astronomica::Script script;for(int id=1;id<=2;++id){Astronomica::Command c;c.opcode=9;c.args.push_back(id);c.delay=0;script.push_back(c);}if(!runner.enqueue(script,50,true))return 7;runner.tick(50);if(runner.executedCount()!=1||runner.pendingCount()!=1)return 8;runner.tick(50);if(runner.executedCount()!=2||runner.pendingCount())return 9;}
 printf("Original delay native verification: PASS (cases%u,aggregate%08x,deferred-zero continuation)\n",cases,aggregate);return 0;
}
