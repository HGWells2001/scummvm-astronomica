"""Replay an exhausted stopped segment even when its saved clock precedes the end."""


def inject(cpp, script):
    old = 'class P512StoppedDecoder final:public Video::QuickTimeDecoder{public:void retainStoppedClock(uint32 ms){_lastTimeChange=Audio::Timestamp(ms);}};'
    assert cpp.count(old) == 1
    cpp = cpp.replace(old + '\n', '')
    decoder = '''class P512StoppedDecoder final : public Video::QuickTimeDecoder {
public:
 void retainStoppedClock(uint32 ms) { _lastTimeChange=Audio::Timestamp(ms); }
 bool stoppedAtSegmentEnd() const {
  // A stopped decoder's independent clock can precede the segment limit.
  // Its next video frame still records whether the segment was exhausted.
  return !isPlaying() && getCurFrame() >= 0 &&
   (!_nextVideoTrack || _nextVideoTrack->endOfTrack() ||
    _nextVideoTrack->getNextFrameStartTime() >= uint32(getEndTime().msecs()));
 }
};
'''
    anchor = 'namespace Astronomica {\n'
    assert cpp.count(anchor) == 1
    cpp = cpp.replace(anchor, anchor + decoder)
    allocation = '_movie = danger ? static_cast<Video::QuickTimeDecoder*>(new P523AudioClockObserver()) : new Video::QuickTimeDecoder();'
    assert cpp.count(allocation) == 1
    cpp = cpp.replace(allocation, '_movie = danger ? static_cast<Video::QuickTimeDecoder*>(new P523AudioClockObserver()) : weather ? new P512StoppedDecoder() : new Video::QuickTimeDecoder();')
    start = cpp.index('   } else if (action.x == 2) {', cpp.index('if (action.opcode == 23 && action.value == 24)'))
    end = cpp.index('   } else { updateMovie();', start)
    body = cpp[start:end]
    predicate = '_movie->endOfVideo() || _movie->getTime() >= uint32(_movie->getEndTime().msecs())'
    assert body.count(predicate) == 1
    body = body.replace(predicate, predicate + ' || static_cast<P512StoppedDecoder*>(_movie)->stoppedAtSegmentEnd()')
    return cpp[:start] + body + cpp[end:], script
