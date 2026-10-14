from pathlib import Path
import shutil
out=Path('outputs/astronomica-cleanroom');engine=out/'engine/astronomica'
p=engine/'script.h';s=p.read_text().replace(' struct SuccessHandler {', ''' struct SoundHandler {
  virtual ~SoundHandler() {}
  virtual bool isBlockingSound(int id) const = 0;
  virtual uint32 onBlockingSound(int id, uint32 now) = 0;
 };
 void setSoundHandler(SoundHandler *handler) { _soundHandler = handler; }
 struct SuccessHandler {''').replace(' SuccessHandler *_successHandler = nullptr;', ' SoundHandler *_soundHandler = nullptr;\n SuccessHandler *_successHandler = nullptr;');p.write_text(s)
p=engine/'script.cpp';s=p.read_text().replace('_successHandler = nullptr; _successGlobal = -1;', '_successHandler = nullptr; _soundHandler = nullptr; _successGlobal = -1;')
s=s.replace('  bool result = true, skipElse = false;', '''  bool result = true, skipElse = false;
  const bool blockingSound = c.opcode == 9 && _soundHandler && _soundHandler->isBlockingSound(c.args[0]-1);
  if (blockingSound) now = _soundHandler->onBlockingSound(c.args[0]-1, now);''')
s=s.replace('c.opcode == 10 || c.opcode == 9 || c.opcode == 5', 'c.opcode == 10 || (c.opcode == 9 && !blockingSound) || c.opcode == 5')
marker=' Common::Array<bool> sounds; sounds.resize(900);'
test=''' // Synchronous sound finishes before the next command's relative timer starts.
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
'''
assert marker in s;s=s.replace(marker,test+marker);p.write_text(s)
p=engine/'astronomica.h';s=p.read_text().replace('public ScriptRunner::SuccessHandler {','public ScriptRunner::SuccessHandler, public ScriptRunner::SoundHandler {').replace(' uint32 onPuzzleSuccess(uint32 now) override;', ''' bool isBlockingSound(int id) const override;
 uint32 onBlockingSound(int id, uint32 now) override;
 uint32 _lastBlockingSoundEnd = 0;
 uint32 onPuzzleSuccess(uint32 now) override;''');p.write_text(s)
p=engine/'astronomica.cpp';s=p.read_text().replace('   // Original exceptions play synchronously; don\'t silently make them async.\n   if ((_place == 505 && id >= 2 && id <= 10) || (_place == 512 && id == 14)) continue;','')
s=s.replace(' _runner.setSoundTargets(targets);', ''' _runner.setSoundTargets(targets);
 if (ConfMan.hasKey("astronomica_audio") && ConfMan.getBool("astronomica_audio")) _runner.setSoundHandler(this);''')
a=s.index('uint32 AstronomicaEngine::onPuzzleSuccess(uint32 now) {');b=s.index('bool AstronomicaEngine::verifyAudio()',a)
s=s[:a]+'''bool AstronomicaEngine::isBlockingSound(int id) const {
 // _playSound 9:3bb5-3be9 selects synchronous flags for these local files.
 return (_place == 505 && id >= 2 && id <= 10) || (_place == 512 && id == 14);
}
uint32 AstronomicaEngine::onBlockingSound(int id, uint32 now) {
 applyScriptActions(now);
 const uint32 started = _system->getMillis();
 if (playSound(id,now)) {
  while (_mixer->isSoundHandleActive(_soundHandle) && !shouldQuit()) {
   Common::Event event;
   while (_system->getEventManager()->pollEvent(event))
    if (event.type == Common::EVENT_QUIT) quitGame();
   _system->updateScreen();
   _system->delayMillis(5);
  }
 }
 _lastBlockingSoundEnd = now + uint32(_system->getMillis() - started);
 return _lastBlockingSoundEnd;
}
uint32 AstronomicaEngine::onPuzzleSuccess(uint32 now) {
 _lastSuccessEnd = onBlockingSound(912,now);
 ++_puzzlesCompleted;
 return _lastSuccessEnd;
}
'''+s[b:]
marker='  bool skyOK = true;'
test='''  // P505: all eight original prompts, using rectangle clicks only.
  bool historyOK = true;
  for (uint wrong = 0; wrong < 2; ++wrong) {
   _runner.resetGlobals(); _runner.seedRandom(1);
   historyOK = loadPlace(505) && historyOK;
   const uint completedBefore = _puzzlesCompleted;
   historyOK = _runner.enqueueStartup(_scene.scripts,0,true) == 3 && historyOK;
   uint32 now = 0;
   auto settle = [&]() {
    uint pass = 0;
    while (_runner.pendingCount() && pass++ < 3000) {
     runScriptsAt(now); animateSpritesAt(now); now += 50;
    }
    return !_runner.pendingCount() && !_runner.clicksBlocked();
   };
   historyOK = settle() && historyOK;
   const int correctRects[] = {9,4,1,8,7,3,5,6};
   for (uint answer = 0; answer < (wrong ? 3U : 8U) && _place == 505; ++answer) {
    int32 prompt = 0;
    if (!_runner.getValue(1,0,prompt) || prompt < 1 || prompt > 8) { historyOK = false; break; }
    const MouseRect &r = _scene.mouseRects[wrong ? 2 : correctRects[prompt-1]];
    const int x = (r.rect[0]+r.rect[2])/2, y = (r.rect[1]+r.rect[3])/2;
    historyOK = spriteAt(x,y) == -1 && !_runner.clicksBlocked() && historyOK;
    clickAtTime(x,y,now);
    historyOK = _runner.pendingCount() > 0 && settle() && historyOK;
    if (_place == 505) {
     int32 errors = -1;
     historyOK = _runner.getValue(1,2,errors) && errors == (wrong ? int32(answer+1) : 0) && historyOK;
    }
   }
   int32 solved = -1;
   historyOK = _place == (wrong ? 321 : 520) && _runner.getValue(0,22,solved) && solved == (wrong ? 0 : 1) &&
    _puzzlesCompleted == completedBefore+(wrong ? 0 : 1) && historyOK;
   debug("Astronomica P505 route %u: %s (destination P%d, success=%d)",wrong,historyOK ? "PASS" : "FAIL",_place,solved);
  }
  debug("Astronomica P505 interaction verification: %s (eight original prompts, blocking speech, image clicks, three-error exit; P520 movie not implemented)",historyOK ? "PASS" : "FAIL");
  scriptsOK = historyOK && scriptsOK;
'''
assert marker in s;s=s.replace(marker,test+marker);p.write_text(s)
for f in engine.iterdir():shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
