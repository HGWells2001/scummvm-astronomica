from speech_duck_probe_nov19 import observe as previous
from speech_duck_expectations_nov19 import adapt

def observe(cpp,header):
 cpp,header=previous(cpp,header);cpp=adapt(cpp)
 # P101 is another mode1 room in the same region;P104 is a mode3 close-up.
 cpp=cpp.replace('loadPlace(104,false,true)','loadPlace(101,false,true)')
 old='  const bool payload=loaded&&_mixer->isSoundHandleActive(_musicHandle)&&_unduckedMusicVolume==-1&&_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)==77;'
 new='''  debug("Speech duck payload detail: wrote%d loaded%d bytes%u canSave%d canLoad%d pending%u loop%d music%d sound%d duck%d volume%d",int(wrote),int(loaded),uint(saved.size()),int(canSaveGameStateCurrently()),int(canLoadGameStateCurrently()),_runner.pendingCount(),_loopSound,int(_mixer->isSoundHandleActive(_musicHandle)),int(_mixer->isSoundHandleActive(_soundHandle)),_unduckedMusicVolume,_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType));
'''+old
 assert cpp.count(old)==1;return cpp.replace(old,new),header
