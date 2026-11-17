"""Preserve mixing ownership for restored P512/P525 ambience and skip logos on direct save loading."""
from restored_music_owner_source_nov17 import production as observe

def production(cpp,header):
 old='const int startPlace = ConfMan.hasKey("astronomica_start_place") ? ConfMan.getInt("astronomica_start_place") : 0;'
 assert cpp.count(old)==1
 cpp=cpp.replace(old,'const int startPlace = ConfMan.hasKey("astronomica_start_place") ? ConfMan.getInt("astronomica_start_place") : (ConfMan.hasKey("save_slot")&&ConfMan.getInt("save_slot")>=0?1:0);')
 for owner in ('out','p'):
  old='_mixer->playStream(Audio::Mixer::kMusicSoundType,&_soundHandle,'+owner+'.ambient);'
  assert cpp.count(old)==1
  cpp=cpp.replace(old,old+'_musicHandle=_soundHandle;')
 return observe(cpp,header)
