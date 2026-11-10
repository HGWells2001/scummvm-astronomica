"""Apply the original P512 voice-before-result ordering and a focused regression."""
def harden(code):
 old='''     if (sound != -2) _values[1][5] = sound == -1;
     if (sound >= 0) {
      if (_soundHandler->isBlockingSound(sound)) now = _soundHandler->onBlockingSound(sound,now);
      else { Action response = {9,sound,0,0}; _actions.push_back(response); }
     }
'''
 new='''     if (sound >= 0) {
      if (_soundHandler->isBlockingSound(sound)) now = _soundHandler->onBlockingSound(sound,now);
      else { Action response = {9,sound,0,0}; _actions.push_back(response); }
     }
     // Original custom24/0 stores local5 after the error voice returns.
     // A synchronous voice must still observe the preceding answer result.
     if (sound != -2) _values[1][5] = sound == -1;
'''
 assert code.count(old)==1
 return code.replace(old,new)

def add_regression(code):
 entry='bool verifyConditions() {';assert code.count(entry)==1
 test=r'''
static bool verifyWeatherVoiceOrder() {
 struct Voice : ScriptRunner::SoundHandler {
  ScriptRunner &runner;uint calls=0;int32 observed=-1;int sound=-1;bool blocking;
  Voice(ScriptRunner&r,bool b):runner(r),blocking(b){}
  bool isBlockingSound(int)const override{return blocking;}
  uint32 onBlockingSound(int id,uint32 now)override{++calls;sound=id;runner.getValue(1,5,observed);return now+17;}
 };
 // Original P512 custom24/0: a previous accepted result remains visible to
 // the wrong-answer voice; only the returned callback is followed by zero.
 for(uint mode=0;mode<2;++mode) {
  ScriptRunner runner;Voice voice(runner,mode!=0);runner.setWeatherSupport(true);runner.setSoundHandler(&voice);
  Common::Array<bool> sounds;sounds.resize(13);for(uint i=0;i<sounds.size();++i)sounds[i]=true;runner.setSoundTargets(sounds);
  for(int i=0;i<6;++i)runner.defineValue(1,i,0);
  runner.defineValue(1,4,1);runner.defineValue(1,5,1);
  Script script;Command c;c.opcode=23;c.delay=-1;c.args.push_back(24);for(uint i=0;i<5;++i)c.args.push_back(0);script.push_back(c);
  if(!runner.start(script,0xfffffff8U,true)||!valueIs(runner,1,5,0))return false;
  ScriptRunner::Action action;
  if(mode) {if(voice.calls!=1||voice.sound!=10||voice.observed!=1||runner.popAction(action))return false;}
  else {if(voice.calls||!runner.popAction(action)||action.opcode!=9||action.value!=10||runner.popAction(action))return false;}
  // A correct setting stores one without a voice. An unknown scenario
  // leaves the previous result intact and does not enqueue a sound.
  runner.defineValue(1,2,15);
  const uint calls=voice.calls;
  if(!runner.start(script,0,true)||!valueIs(runner,1,5,1)||voice.calls!=calls||runner.popAction(action))return false;
  runner.defineValue(1,4,0);
  if(!runner.start(script,0,true)||!valueIs(runner,1,5,1)||voice.calls!=calls||runner.popAction(action))return false;
 }
 return true;
}
'''
 return code.replace(entry,test+'\n'+entry+'\n if(!verifyWeatherVoiceOrder())return false;')
