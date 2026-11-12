"""Keep the original predicate untouched and log its state only after refusal."""
from p512_memory_refusal_source_nov12b import inject as previous


def inject(cpp, script):
    cpp, script = previous(cpp, script)
    anchor = 'if(_place!=512||_p512OriginalPlays!=plays+1||_p512OriginalSeekSerial<=seeks||_p512NeedsOriginalSeek||_p512PlayWithoutRequiredSeek||!_moviePlaying||!_movie->isPlaying()||_movie->getTime()>=uint32(_movie->getEndTime().msecs())){'
    assert cpp.count(anchor) == 1
    observation = 'debug("P512 refused post-Play state: scenario%u mask%u place%d plays%u/%u seeks%u/%u need%d unordered%u enginePlaying%d decoderPlaying%d time%u end%u clock%u pending%u blocked%d",words[15],words[kP512Runner+309],_place,_p512OriginalPlays,plays,_p512OriginalSeekSerial,seeks,int(_p512NeedsOriginalSeek),_p512PlayWithoutRequiredSeek,int(_moviePlaying),int(_movie&&_movie->isPlaying()),_movie?_movie->getTime():0,_movie?uint32(_movie->getEndTime().msecs()):0,logical,_runner.pendingCount(),int(_runner.clicksBlocked()));'
    return cpp.replace(anchor, anchor + observation), script
