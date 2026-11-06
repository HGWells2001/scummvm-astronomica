// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef VIDEO_PAUSED_AUDIO_GATE_H
#define VIDEO_PAUSED_AUDIO_GATE_H

#include "audio/audiostream.h"
#include "audio/mixer.h"
#include "common/mutex.h"

namespace Video {

// A newly admitted paused track must not advance its source in the interval
// between playStream() and pauseHandle(). Silence may enter the mixer during
// that interval; the original stream remains untouched until the gate is armed.
class PausedAudioGate final : public Audio::AudioStream {
public:
 PausedAudioGate(Audio::AudioStream *source, DisposeAfterUse::Flag dispose)
  : _source(source), _dispose(dispose), _armed(false) { assert(source); }
 ~PausedAudioGate() override { if (_dispose == DisposeAfterUse::YES) delete _source; }
 int readBuffer(int16 *buffer, const int samples) override {
  Common::StackLock lock(_mutex);
  if (_armed) return _source->readBuffer(buffer, samples);
  for (int i = 0; i < samples; ++i) buffer[i] = 0;
  return samples;
 }
 bool isStereo() const override { return _source->isStereo(); }
 int getRate() const override { return _source->getRate(); }
 bool endOfData() const override {
  Common::StackLock lock(_mutex); return _armed && _source->endOfData();
 }
 bool endOfStream() const override {
  Common::StackLock lock(_mutex); return _armed && _source->endOfStream();
 }
 void arm() { Common::StackLock lock(_mutex); _armed = true; }
private:
 Audio::AudioStream *_source;
 DisposeAfterUse::Flag _dispose;
 bool _armed;
 mutable Common::Mutex _mutex;
};

// The caller owns this handle's lifecycle and has already stopped it. An
// unarmed gate cannot naturally exhaust; a failed mixer admission may delete
// it synchronously, so never dereference it without verifying the handle.
inline bool playPausedAudioStream(Audio::Mixer *mixer, Audio::Mixer::SoundType type,
 Audio::SoundHandle *handle, Audio::AudioStream *source, byte volume, int8 balance,
 DisposeAfterUse::Flag dispose, uint32 rate) {
 assert(!mixer->isSoundHandleActive(*handle));
 PausedAudioGate *gate = new PausedAudioGate(source, dispose);
 mixer->playStream(type, handle, gate, -1, volume, balance, DisposeAfterUse::YES);
 if (!mixer->isSoundHandleActive(*handle)) return false;
 if (rate) mixer->setChannelRate(*handle, rate);
 mixer->pauseHandle(*handle, true);
 if (!mixer->isSoundHandleActive(*handle)) return false;
 gate->arm();
 return true;
}

} // namespace Video
#endif
