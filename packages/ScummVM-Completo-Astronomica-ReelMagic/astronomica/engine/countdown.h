// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef ASTRONOMICA_COUNTDOWN_H
#define ASTRONOMICA_COUNTDOWN_H
#include "common/scummsys.h"
namespace Astronomica {
struct CountdownResult { int32 mode, stage; int sound, destination; };
inline CountdownResult worldCountdown(int32 mode, int32 item, int32 stage, uint32 started, uint32 now) {
 CountdownResult r = {mode,stage,0,0};
 if (mode == 1) {
  if (item == 1) r.mode = 2;
  const uint32 elapsed = now-started;
  static const uint32 limits[] = {4000,60000,120000,180000,240000,270000,295000};
  if (started && stage >= 0 && stage < 7 && elapsed > limits[stage]) {
   r.stage = stage+1; r.sound = 913+stage; return r;
  }
  if (started && elapsed > 300000) { r.mode = 3; r.destination = 427; }
 } else if (mode == 2 && item == 0) r.mode = 1;
 return r;
}
}
#endif
