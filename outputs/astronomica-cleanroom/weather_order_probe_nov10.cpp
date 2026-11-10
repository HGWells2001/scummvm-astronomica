// SPDX-License-Identifier: GPL-3.0-or-later
// Real ScriptRunner comparison against original weather instruction fixtures.
#define FORBIDDEN_SYMBOL_ALLOW_ALL
#include <cstdio>
#include <cstdlib>
#include "astronomica/script.h"
static uint32 word(FILE*f){byte b[4];if(fread(b,1,4,f)!=4)exit(2);return uint32(b[0])|(uint32(b[1])<<8)|(uint32(b[2])<<16)|(uint32(b[3])<<24);}
struct Voice: Astronomica::ScriptRunner::SoundHandler {
 Astronomica::ScriptRunner *runner;bool blocking;uint calls=0;int sound=-1;int32 observed=-1;
 Voice(Astronomica::ScriptRunner*r,bool b):runner(r),blocking(b){}
 bool isBlockingSound(int)const override{return blocking;}
 uint32 onBlockingSound(int id,uint32 now)override{++calls;sound=id;if(!runner->getValue(1,5,observed))exit(3);return now+17;}
};
int main(int argc,char**argv){
 if(argc!=2)return 2;FILE*f=fopen(argv[1],"rb");if(!f)return 2;char magic[8];if(fread(magic,1,8,f)!=8||memcmp(magic,"WFXO0001",8))return 2;
 const uint cases=word(f);if(!cases||cases>100000)return 2;uint32 aggregate=2166136261U;uint modes=0;
 for(uint row=0;row<cases;++row){
  const int32 scenario=int32(word(f)),a=int32(word(f)),b=int32(word(f)),c=int32(word(f));
  const uint32 initial=word(f),final=word(f),sound=word(f),observed=word(f);if(initial>1||final>1)return 2;
  const int directExpected=scenario<1||scenario>6?-2:sound==0xffffffffU?-1:int(sound);
  if(Astronomica::ScriptRunner::weatherAnswer(scenario,a,b,c)!=directExpected){fprintf(stderr,"FAIL weather pure answer row%u\n",row);return 4;}
  for(uint blocking=0;blocking<2;++blocking){
   Astronomica::ScriptRunner runner;Voice voice(&runner,blocking!=0);runner.setWeatherSupport(true);runner.setSoundHandler(&voice);
   Common::Array<bool> sounds;sounds.resize(923);for(uint i=0;i<sounds.size();++i)sounds[i]=true;runner.setSoundTargets(sounds);
   for(int scope=0;scope<2;++scope)for(int id=0;id<100;++id)if(!runner.defineValue(scope,id,0))return 3;
   runner.defineValue(1,0,a);runner.defineValue(1,1,b);runner.defineValue(1,2,c);runner.defineValue(1,4,scenario);runner.defineValue(1,5,int32(initial));
   Astronomica::Script call;Astronomica::Command cmd;cmd.opcode=23;cmd.delay=-1;cmd.args.push_back(24);for(uint n=0;n<5;++n)cmd.args.push_back(0);call.push_back(cmd);
   if(!runner.start(call,0xfffffff8U,true)){fprintf(stderr,"FAIL weather admission row%u\n",row);return 5;}
   uint actions=0;Astronomica::ScriptRunner::Action action;
   while(runner.popAction(action)){if(blocking||sound==0xffffffffU||action.opcode!=9||uint32(action.value)!=sound){fprintf(stderr,"FAIL weather action row%u\n",row);return 6;}++actions;}
   const uint voices=sound!=0xffffffffU;
   if(actions!=(blocking?0:voices)||voice.calls!=(blocking?voices:0)||runner.executedCount()!=1||runner.pendingCount()){fprintf(stderr,"FAIL weather counts row%u\n",row);return 6;}
   if(blocking&&voices&&(uint32(voice.sound)!=sound||uint32(voice.observed)!=observed)){
    fprintf(stderr,"FAIL weather voice order row%u scenario%d settings%d,%d,%d initial%u: observed%d/%u sound%d/%u\n",row,scenario,a,b,c,initial,voice.observed,observed,voice.sound,sound);return 8;
   }
   for(int scope=0;scope<2;++scope)for(int id=0;id<100;++id){int32 v=0;const uint32 expected=scope? id==0?uint32(a):id==1?uint32(b):id==2?uint32(c):id==4?uint32(scenario):id==5?final:0U:0U;if(!runner.getValue(scope,id,v)||uint32(v)!=expected){fprintf(stderr,"FAIL weather final state row%u scope%d id%d\n",row,scope,id);return 7;}}
   for(uint32 v:{row,blocking,uint32(scenario),uint32(a),uint32(b),uint32(c),initial,final,sound,observed})aggregate=(aggregate^v)*16777619U;++modes;
  }
 }
 if(fgetc(f)!=EOF)return 2;fclose(f);printf("Original weather native PASS:cases%u,modes%u,aggregate%08x\n",cases,modes,aggregate);return 0;
}
