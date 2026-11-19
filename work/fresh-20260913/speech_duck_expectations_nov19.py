"""Update pre-existing audio assertions for the explicitly requested speech-over-Music policy."""
def adapt(cpp):
 def one(old,new):
  nonlocal cpp
  assert cpp.count(old)==1,(old[:100],cpp.count(old));cpp=cpp.replace(old,new)
 one('_mixer->hasActiveChannelOfType(effects) && !_mixer->hasActiveChannelOfType(music) &&','_mixer->hasActiveChannelOfType(effects) && _mixer->hasActiveChannelOfType(music) && _mixer->getChannelVolume(_musicHandle)==128 &&')
 one('foreground replacements, controls %s','speech overlaps, controls %s')
 # A foreground voice keeps the same loop stream, including after completion.
 one('  Script foreground; Command fg;', '  const Audio::SoundHandle continuousLoop=_musicHandle;\n  Script foreground; Command fg;')
 one('  loopOK = _lastSound == 2 && _soundsStarted == beforeLoop+2 && _lastSoundAt == 6000 && loopOK;', '  loopOK = _lastSound == 2 && _soundsStarted == beforeLoop+2 && _lastSoundAt == 6000 && _musicHandle==continuousLoop && _mixer->isSoundHandleActive(continuousLoop) && _mixer->getChannelVolume(continuousLoop)==128 && loopOK;')
 one('  loopOK = _soundsStarted == beforeLoop+3 && _lastSound == 11 && loopOK;','  loopOK = _soundsStarted == beforeLoop+2 && _lastSound == 11 && _musicHandle==continuousLoop && _mixer->getChannelVolume(continuousLoop)==255 && loopOK;')
 one('  loopOK = !_loopEnabled && !_mixer->isSoundHandleActive(_soundHandle) && _soundsStarted == beforeLoop+3 && loopOK;','  loopOK = !_loopEnabled && !_mixer->isSoundHandleActive(_soundHandle) && _soundsStarted == beforeLoop+2 && loopOK;')
 one('  loopOK = _loopEnabled && _soundsStarted == beforeLoop+4 && _mixer->isSoundHandleActive(_soundHandle) && loopOK;','  loopOK = _loopEnabled && _soundsStarted == beforeLoop+3 && _mixer->isSoundHandleActive(_soundHandle) && loopOK;')
 one('   _lastSound == 302 && _soundsStarted == beforeIntro+1 && !_mixer->isSoundHandleActive(_soundHandle) &&','   _lastSound == 0 && _soundsStarted == beforeIntro+2 && _mixer->isSoundHandleActive(_musicHandle) && _mixer->getChannelVolume(_musicHandle)==255 &&')
 one('  entryAudioOK = _soundsStarted == beforeIntro+1 && entryAudioOK;','  entryAudioOK = _soundsStarted == beforeIntro+2 && entryAudioOK;')
 one('  const Audio::SoundHandle music=_musicHandle;const bool started=playSound(911,scriptClock());const bool exclusive=started&&!_mixer->isSoundHandleActive(music);','  const Audio::SoundHandle music=_musicHandle;const bool started=playSound(911,scriptClock());const bool ducked=started&&_musicHandle==music&&_mixer->isSoundHandleActive(music)&&_mixer->getChannelVolume(music)==128;')
 one('  debug("Exploration music narration: exclusive%d resumed%d",int(exclusive),int(resumed));','  debug("Exploration music narration: ducked%d resumed%d",int(ducked),int(resumed));')
 one('  playSound(911,scriptClock());const bool voice=!_mixer->isSoundHandleActive(_musicHandle)&&_mixer->isSoundHandleActive(_soundHandle);','  playSound(911,scriptClock());const bool voice=_mixer->isSoundHandleActive(_musicHandle)&&_mixer->getChannelVolume(_musicHandle)==128&&_mixer->isSoundHandleActive(_soundHandle);')
 one('P504 speed narration foreground:','P504 speed narration ducked:')
 one('int(!_mixer->isSoundHandleActive(_musicHandle)&&_mixer->isSoundHandleActive(_soundHandle))','int(_mixer->isSoundHandleActive(_musicHandle)&&_mixer->getChannelVolume(_musicHandle)==128&&_mixer->isSoundHandleActive(_soundHandle))') if cpp.count('int(!_mixer->isSoundHandleActive(_musicHandle)&&_mixer->isSoundHandleActive(_soundHandle))')==1 else None
 # Both P513 and shared-door observers have the same old exclusivity expression.
 expr='int(!_mixer->isSoundHandleActive(_musicHandle)&&_mixer->isSoundHandleActive(_soundHandle))'
 cpp=cpp.replace(expr,'int(_mixer->isSoundHandleActive(_musicHandle)&&_mixer->getChannelVolume(_musicHandle)==128&&_mixer->isSoundHandleActive(_soundHandle))')
 cpp=cpp.replace('P513 numeric narration foreground:','P513 numeric narration ducked:').replace('Door Music narration foreground:','Door Music narration ducked:')
 one('   const bool exclusive=!_mixer->isSoundHandleActive(owner)&&_mixer->isSoundHandleActive(_soundHandle);','   const bool ducked=_musicHandle==owner&&_mixer->isSoundHandleActive(owner)&&_mixer->getChannelVolume(owner)==128&&_mixer->isSoundHandleActive(_soundHandle);')
 one('   const bool continuity=!effect||(_musicHandle==owner&&_mixer->isSoundHandleActive(owner)&&_mixer->getSoundElapsedTime(owner)>=elapsed);','   const bool continuity=_musicHandle==owner&&_mixer->isSoundHandleActive(owner)&&_mixer->getSoundElapsedTime(owner)>=elapsed;')
 one('(effect?overlap:exclusive)&&continuity','(effect?(overlap&&_mixer->getChannelVolume(owner)==255):ducked)&&continuity')
 one('effect%d role%d overlap%d exclusive%d continuous%d result%d','effect%d role%d overlap%d ducked%d continuous%d result%d')
 one('int(overlap),int(exclusive),int(continuity)','int(overlap),int(ducked),int(continuity)')
 return cpp
