"""Extend the real engine with bounded idle P281 retained-round native saves."""
PRODUCTION=r'''
// ASVM32: the idle P281 gateway may retain a partly visited variant bag.
enum { kP281Words=12+27+ScriptRunner::kPersistentStateWords+16 };
static bool p281State(const Common::Array<uint32>&s) {
 if(!ScriptRunner::validPersistentState(s)||s[603]<1)return false;
 for(uint i=0;i<100;++i)if(s[3*i+2]!=1||(s[3*i+1]&&(i>=3||s[3*i+1]!=6))||s[301+3*i]||s[302+3*i])return false;
 return true;
}
static bool p281Scene(const Scene&s) {
 if(s.mode!=1||s.layers!=1||s.nav[0]!=286||s.nav[1]||s.nav[2]!=276||s.sprites.size()!=1||s.conditions.size()!=3||!s.scripts.empty()||!s.movies.empty()||!s.mouseRects.empty()||spriteFrameCount(s,0)!=2)return false;
 const int declarations[3][6]={{0,0,6,1,1,6},{0,1,6,0,0,63},{0,2,6,0,0,63}};for(uint i=0;i<3;++i)for(uint j=0;j<6;++j)if(s.conditions[i].raw[j]!=declarations[i][j])return false;
 const Sprite&x=s.sprites[0];if(x.clone!=-1||x.layer!=1||!x.visible||x.x!=23||x.y!=365||x.autoFrame||x.autoMove||x.dragEnabled||x.cursor||x.planetMotion||x.planetPeriod!=-1||!x.mouseIn.empty()||!x.mouseOut.empty()||!x.clickEnabled||x.clickType!=2||x.click.size()!=2)return false;
 const Command&a=x.click[0],&b=x.click[1];if(a.opcode!=9||a.delay||a.args.size()!=1||a.args[0]!=2||!a.text.empty()||b.opcode!=23||b.delay!=5000||b.args.size()!=6||b.args[0]!=17||!b.text.empty())return false;
 for(uint i=1;i<6;++i)if(b.args[i])return false;return true;
}
static bool p281Sprite(const Common::Array<uint32>&w,const Scene&s) {
 if(w.size()!=27||!p281Scene(s))return false;Sprite initial=s.sprites[0];initial.selectedFrame=0;Common::Array<uint32>base;p526SpriteWords(initial,base);return w==base;
}
static bool p281Dimensions(const Common::Array<uint32>&w) {
 if(w.size()!=16)return false;const uint widths[]={50,39,110,60,60,110,39,50},heights[]={50,100,40,60,60,40,100,50};bool empty=true,configured=true;
 for(uint i=0;i<8;++i){empty&=!w[i]&&!w[8+i];configured&=w[i]==widths[i]&&w[8+i]==heights[i];}return empty||configured;
}
bool AstronomicaEngine::canSaveP281Persistent()const {
 if(_place!=281||!_runner.scriptsIdle()||!_runner.variantRound()||!p281Scene(_scene)||_questionSaveBaseline.size()!=1||_movie||_movieFrame.w||_pendingImage.w||!_pendingImageName.empty()||!_displayedImageName.empty()||_loopSound!=-1||!_loopEnabled||_mixer->isSoundHandleActive(_soundHandle))return false;
 for(const char*option:{"astronomica_audio","astronomica_animation","astronomica_sprite_input"})if(!ConfMan.hasKey(option)||!ConfMan.getBool(option))return false;
 if(!_runner.canRun(_scene.sprites[0].click,true)||_comet.frame<0||_comet.frame>12||_comet.previousFrame<0||_comet.previousFrame>12||_lastSound< -1||_lastSound>922||_ball.scenario||_ball.centerX||_ball.centerY||_ball.side!=2||_ball.period!=10)return false;
 Common::Array<uint32>state,sprite,extra;if(!_runner.exportPersistentState(state)||!p281State(state))return false;p516Extra(extra);if(!validP501Extra(extra))return false;
 p526SpriteWords(_scene.sprites[0],sprite);Scene original=_scene;original.sprites=_questionSaveBaseline;return p281Sprite(sprite,original);
}
Common::Error AstronomicaEngine::saveP281Persistent(Common::WriteStream*stream) {
 if(!canSaveP281Persistent())return Common::kWritingFailed;
 const uint32 header[]={281,_puzzlesCompleted,scriptClock(),uint32(_previousPlace),_lastSoundAt,uint32(_comet.frame),uint32(_comet.previousFrame),uint32(_lastSound),_lastBlockingSoundEnd,_lastSuccessEnd,0,0};
 Common::Array<uint32>state,sprite;_runner.exportPersistentState(state);p526SpriteWords(_scene.sprites[0],sprite);
 stream->writeUint32BE(MKTAG('A','S','V','M'));stream->writeUint32LE(32);uint32 hash=2166136261U;
 auto put=[&](uint32 v){stream->writeUint32LE(v);hash=(hash^v)*16777619U;};for(uint32 v:header)put(v);for(uint32 v:sprite)put(v);for(uint32 v:state)put(v);for(int v:_jupiterWidths)put(uint32(v));for(int v:_jupiterHeights)put(uint32(v));stream->writeUint32LE(hash);
 return stream->err()?Common::kWritingFailed:Common::kNoError;
}
Common::Error AstronomicaEngine::loadP281Persistent(Common::SeekableReadStream*stream) {
 if(stream->size()-stream->pos()<(kP281Words+1)*4)return Common::kReadingFailed;
 for(const char*option:{"astronomica_audio","astronomica_animation","astronomica_sprite_input"})if(!ConfMan.hasKey(option)||!ConfMan.getBool(option))return Common::kReadingFailed;
 uint32 h[12],hash=2166136261U;auto get=[&](){const uint32 v=stream->readUint32LE();hash=(hash^v)*16777619U;return v;};for(uint32&v:h)v=get();
 Common::Array<uint32>sprite,state,dimensions;sprite.resize(27);state.resize(605);dimensions.resize(16);for(uint32&v:sprite)v=get();for(uint32&v:state)v=get();for(uint32&v:dimensions)v=get();
 if(stream->readUint32LE()!=hash||stream->err()||h[0]!=281||(h[3]>537&&h[3]!=0xffffffffU)||h[5]>12||h[6]>12||(h[7]>922&&h[7]!=0xffffffffU)||h[10]||h[11]||!p281State(state)||!p281Dimensions(dimensions))return Common::kReadingFailed;
 Common::File file;const Common::Path root=ConfMan.getPath("path"),path=root.join("PLACES/P281/MEGAFILE.HYP");
 if(!universeFileIdentity(path,305663,2533576351U)||!file.open(Common::FSNode(path)))return Common::kReadingFailed;
 Scene parsed;ResourceReader reader(file);if(!reader.read(parsed)||!p281Sprite(sprite,parsed))return Common::kReadingFailed;
 for(const Common::String&name:{Common::String("PLACES/P281/S1.WAV"),Common::String("SOUNDS/S12.WAV"),Common::String("SOUNDS/S22.WAV")}) {
  Common::File voice;if(!voice.open(Common::FSNode(root.join(Common::Path(name)))))return Common::kReadingFailed;int size,rate;byte flags;uint16 type;if(!Audio::loadWAVFromStream(voice,size,rate,flags,&type)||type!=1)return Common::kReadingFailed;
 }
 if(!loadPlace(281,false,true))return Common::kReadingFailed;
 if(!_runner.importPersistentState(state))error("Validated P281 retained-round state could not be installed");
 _puzzlesCompleted=h[1];_pausedMillis=(_clockPaused?_pauseStarted:_system->getMillis())-h[2];_previousPlace=int32(h[3]);_lastSoundAt=h[4];_comet.frame=int32(h[5]);_comet.previousFrame=int32(h[6]);_lastSound=int32(h[7]);_lastBlockingSoundEnd=h[8];_lastSuccessEnd=h[9];
 for(uint i=0;i<8;++i){_jupiterWidths[i]=int32(dimensions[i]);_jupiterHeights[i]=int32(dimensions[8+i]);}p526RestoreSprite(_scene.sprites[0],&sprite[0]);redrawSprites();return Common::kNoError;
}
'''

def production(cpp,header):
 anchor='bool AstronomicaEngine::canSaveVariant() const {';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,PRODUCTION+'\n'+anchor)
 anchor='const bool enabled = canSaveP523()';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,'const bool enabled = canSaveP281Persistent() || canSaveP523()')
 anchor=' if (_place == 525) return saveP525(stream);';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,anchor+'\n if (_place == 281 && _runner.variantRound()) return saveP281Persistent(stream);')
 anchor=' if (version == 31) return loadP523(stream);';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,' if (version == 32) return loadP281Persistent(stream);\n'+anchor)
 anchor='_questionSaveBaseline.clear(); if (place == 501';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,'_questionSaveBaseline.clear(); if (place == 281 || place == 501')
 anchor=' bool verifyP281ReturnRounds();';assert header.count(anchor)==1
 header=header.replace(anchor,anchor+'\n bool canSaveP281Persistent()const;\n Common::Error saveP281Persistent(Common::WriteStream*stream);\n Common::Error loadP281Persistent(Common::SeekableReadStream*stream);\n bool verifyP281PersistentBoundary(uint route,uint round);\n bool verifyP281PersistentFile();')
 return cpp,header

TESTS=r'''
bool AstronomicaEngine::verifyP281PersistentBoundary(uint route,uint round) {
 auto snapshot=[&](Common::Array<byte>&bytes){Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(saveGameStream(&out).getCode()!=Common::kNoError)return false;bytes.clear();for(uint i=0;i<out.size();++i)bytes.push_back(out.getData()[i]);return true;};
 auto restore=[&](const Common::Array<byte>&bytes){Common::MemoryReadStream in(bytes.empty()?nullptr:&bytes[0],bytes.size());return loadGameStream(&in).getCode()==Common::kNoError;};
 auto fingerprint=[&](){Common::Array<uint32>s,w;_runner.exportPersistentState(s);for(const Sprite&x:_scene.sprites)p526SpriteWords(x,w);uint32 h=2166136261U;for(uint32 v:s)h=(h^v)*16777619U;for(uint32 v:w)h=(h^v)*16777619U;for(int v:_jupiterWidths)h=(h^uint32(v))*16777619U;for(int v:_jupiterHeights)h=(h^uint32(v))*16777619U;for(uint32 v:{uint32(_place),_puzzlesCompleted,uint32(_previousPlace),_lastSoundAt,uint32(_lastSound),_lastBlockingSoundEnd,_lastSuccessEnd,uint32(_comet.frame),uint32(_comet.previousFrame)})h=(h^v)*16777619U;return(h^screenRGBHash(_screen))*16777619U;};
 if(route==1){const int widths[]={50,39,110,60,60,110,39,50},heights[]={50,100,40,60,60,40,100,50};for(uint i=0;i<8;++i){_jupiterWidths[i]=widths[i];_jupiterHeights[i]=heights[i];}_comet.frame=3;_comet.previousFrame=4;}
 if(!canSaveP281Persistent()){debug("P281 retained canSave: FAIL (round%u,loop%d,enabled%d,active%d,baseline%u)",round,_loopSound,int(_loopEnabled),int(_mixer->isSoundHandleActive(_soundHandle)),_questionSaveBaseline.size());return false;}
 Common::Array<byte>bytes;if(!snapshot(bytes)||bytes.size()!=2652||READ_LE_UINT32(&bytes[4])!=32)return false;
 const uint32 before=fingerprint();
 if(route==0&&round==1){
  const uint32 unchanged=p510WholeLiveHash();const uint sounds=_soundsStarted;const void*pixels=_screen.getPixels();
  auto refuse=[&](const Common::Array<byte>&bad){return !restore(bad)&&p510WholeLiveHash()==unchanged&&_soundsStarted==sounds&&_screen.getPixels()==pixels;};
  for(uint length=0;length<bytes.size();++length){Common::Array<byte>bad;for(uint i=0;i<length;++i)bad.push_back(bytes[i]);if(!refuse(bad)){debug("P281 truncate: FAIL at%u",length);return false;}}
  Common::Array<byte>bad=bytes;for(uint i=0;i<bad.size();++i){bad[i]^=0x80;if(!refuse(bad)){debug("P281 corruption: FAIL at%u",i);return false;}bad[i]^=0x80;}
  const uint invalid[]={0,3,5,6,7,10,11,12,13,14,16,18,25,30,39+1,39+2,39+10,39+301,39+302,39+602,39+603,39+604,644};
  for(uint index:invalid){bad=bytes;WRITE_LE_UINT32(&bad[8+index*4],0x80000000U);uint32 h=2166136261U;for(uint i=0;i<kP281Words;++i)h=(h^READ_LE_UINT32(&bad[8+i*4]))*16777619U;WRITE_LE_UINT32(&bad[bad.size()-4],h);if(!refuse(bad)){debug("P281 field: FAIL at%u",index);return false;}}
  for(const char*option:{"astronomica_audio","astronomica_animation","astronomica_sprite_input"}){ConfMan.setBool(option,false);const uint32 disabled=p510WholeLiveHash();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);if(canSaveP281Persistent()||saveGameStream(&out).getCode()==Common::kNoError||out.size()||restore(bytes)||p510WholeLiveHash()!=disabled)return false;ConfMan.setBool(option,true);}
  debug("P281 retained codec refusals: PASS (2652 truncations,2652 single-byte corruptions,%u rehashed semantic fields,three disabled modes)",uint(ARRAYSIZE(invalid)));
 }
 if(!loadPlace(286,false,true))return false;_runner.resetVariantSequence();_runner.seedRandom(888);_puzzlesCompleted=123;_comet.frame=8;_comet.previousFrame=9;
 if(!restore(bytes)||_place!=281||_runner.variantRound()!=round||!canSaveP281Persistent()||fingerprint()!=before){debug("P281 retained roundtrip: FAIL route%u round%u",route,round);return false;}
 if(route==0&&round==1){
  if(!loadPlace(512,false,true)||!_movie)return false;
  {PauseToken outer=pauseEngine(),inner=pauseEngine();if(!restore(bytes)||!_clockPaused||_movie||scriptClock()!=READ_LE_UINT32(&bytes[16]))return false;inner.clear();if(!_clockPaused)return false;outer.clear();}
  if(_clockPaused||!canSaveP281Persistent()||fingerprint()!=before)return false;
  debug("P281 retained paused recipient: PASS (foreign decoder retired,two caller tokens retained,logical epoch restored)");
 }
 // A pending old gateway voice/selection must be retired by a valid load.
 clickAtTime(37,384,scriptClock());runScriptsAt(scriptClock());if(!_runner.pendingCount())return false;const uint starts=_soundsStarted;
 if(!restore(bytes)||_runner.pendingCount()||_soundsStarted!=starts||fingerprint()!=before||_mixer->isSoundHandleActive(_soundHandle))return false;
 runScriptsAt(scriptClock()+6000);if(_place!=281||_runner.variantRound()!=round||fingerprint()!=before)return false;
 if(saveGameState(40+route*3+round,"P281 retained variant round").getCode()!=Common::kNoError)return false;
 Common::Array<uint32>s;_runner.exportPersistentState(s);debug("P281 retained physical boundary: PASS (slot%u,route%u,round%u,mask%u,fingerprint%08x)",40+route*3+round,route,round,s[604],before);return true;
}
bool AstronomicaEngine::verifyP281PersistentFile() {
 if(!canSaveP281Persistent())return false;const uint count=_puzzlesCompleted,firstRound=_runner.variantRound();int32 prior=0;if(!_runner.getValue(0,23,prior))return false;
 Common::Array<uint32>state;_runner.exportPersistentState(state);uint mask=state[604];
 auto settle=[&](){const uint32 began=_system->getMillis();while(_runner.pendingCount()&&_system->getMillis()-began<90000&&!shouldQuit()){runScriptsAt(scriptClock());animateSpritesAt(scriptClock());_system->delayMillis(5);}return !_runner.pendingCount()&&!_runner.clicksBlocked()&&!shouldQuit();};
 for(uint round=firstRound;round<=3;++round){
  const uint32 start=scriptClock();clickAtTime(37,384,start);const uint32 began=_system->getMillis();
  while(_place==281&&_system->getMillis()-began<30000&&!shouldQuit()){runScriptsAt(scriptClock());animateSpritesAt(scriptClock());_system->delayMillis(5);}
  if(_place==281||scriptClock()-start<5000||!settle())return false;
  if(round==3)break;
  if(!(_place==506||(_place>=531&&_place<=535))||_runner.variantRound()!=round+1||!_runner.exportPersistentState(state)||(state[604]&mask)!=mask||state[604]==mask)return false;
  mask=state[604];clickAtTime(24,417,scriptClock());if(!settle()||_place!=281||!canSaveP281Persistent())return false;
 }
 int32 solved=0;const bool ok=_place==519&&!_runner.variantRound()&&_runner.getValue(0,23,solved)&&solved==1&&_puzzlesCompleted==count+uint(prior==0);
 debug("P281 retained fresh continuation: %s (startRound%u,priorGlobal%d,P%d,count%u,original gateway/unsolved controls)",ok?"PASS":"FAIL",firstRound,prior,_place,_puzzlesCompleted);return ok;
}
'''

def tests(cpp):
 anchor='bool AstronomicaEngine::verifyP281ReturnRounds(){';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,TESTS+'\n'+anchor)
 old='if(!refused("returned nonzero round",route,round))return fail("nonzero round save");';assert cpp.count(old)==1;cpp=cpp.replace(old,'if(!verifyP281PersistentBoundary(route,round))return fail("retained round save");')
 cpp=cpp.replace('six actual unsolved exits,two idle v2 loads,fourteen zero-byte refusals,first/repeated completion','six actual unsolved exits,two idle v2 loads,eight pending zero-byte refusals,six ASVM32 saves,first/repeated completion')
 anchor=' if (ConfMan.hasKey("astronomica_verify_p512") && ConfMan.getBool("astronomica_verify_p512")) {';assert cpp.count(anchor)==1
 branch=r'''
 if(ConfMan.hasKey("astronomica_verify_p281_saves")&&ConfMan.getBool("astronomica_verify_p281_saves")) {
  ConfMan.setBool("astronomica_audio",true);ConfMan.setBool("astronomica_animation",true);ConfMan.setBool("astronomica_sprite_input",true);ConfMan.setBool("astronomica_entry_scripts",true);
  const bool fresh=ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")>=41&&ConfMan.getInt("save_slot")<=46;
  const bool ok=fresh?verifyP281PersistentFile():verifyP281ReturnRounds();_background.free();_screen.free();quitGame();return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"P281 retained saves verification failed");
 }
'''
 return cpp.replace(anchor,branch+'\n'+anchor)
