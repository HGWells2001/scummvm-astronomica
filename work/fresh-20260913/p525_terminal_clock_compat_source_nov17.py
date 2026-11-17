"""Extend low-clock admission without narrowing the existing high-clock save domain."""
from p525_terminal_clock_source_nov17 import production as strict

def production(cpp,header):
 cpp,header=strict(cpp,header)
 old='if(frameStart>=rangeEnd||w[9]<frameStart||!p.decoder->decodeNextFrame()||p.decoder->getCurFrame()!=int32(w[10])||stopped->nextFrameStartForClockObservation()<rangeEnd)return false;'
 new='''if(!p.decoder->decodeNextFrame()||p.decoder->getCurFrame()!=int32(w[10]))return false;
 // Preserve prior high-clock saves: playback can stop on elapsed time
 // before drawing the final frame. Only the newly admitted low clocks
 // need an exhausted final-frame witness.
 if(w[9]<rangeEnd&&(frameStart>=rangeEnd||w[9]<frameStart||stopped->nextFrameStartForClockObservation()<rangeEnd))return false;'''
 assert cpp.count(old)==1;cpp=cpp.replace(old,new)
 old='bad[10]=frame;bad[9]=80066;'
 assert cpp.count(old)==1;cpp=cpp.replace(old,'bad[10]=frame;bad[9]=w[13]*1000/30-1;')
 anchor='   Common::Array<uint32>low=w;low[9]=low[13]*1000/30-1;'
 extra=r'''
   Common::Array<uint32>legacy=w;legacy[10]=w[10]-1;legacy[9]=legacy[13]*1000/30;legacy.back()=p525StoppedHash(legacy);
   const uint32 oldHash=p510WholeLiveHash();P525StoppedPrepared oldPrepared;
   const bool admitted=prepareP525Stopped(legacy,oldPrepared)&&oldPrepared.ready&&oldPrepared.decoder->getCurFrame()==int32(legacy[10])&&oldPrepared.decoder->getTime()==legacy[9]&&p510WholeLiveHash()==oldHash;
   debug("P525 terminal legacy high-clock admission: frame%u admitted%d",legacy[10],int(admitted));ok=admitted&&ok;
'''
 assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,extra+'\n'+anchor)
 return cpp,header
