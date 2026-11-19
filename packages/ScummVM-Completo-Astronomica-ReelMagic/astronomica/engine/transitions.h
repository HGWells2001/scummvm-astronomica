// SPDX-License-Identifier: GPL-3.0-or-later
// ASTRO.EXE _do_place, 9:0289-066c. See probe_transitions.py.
#ifndef ASTRONOMICA_TRANSITIONS_H
#define ASTRONOMICA_TRANSITIONS_H
#include "common/scummsys.h"
namespace Astronomica {
struct PlaceTransition {
 int destination;
 int32 permit;
 bool failureVoice;
 int immediateSound;
};
inline PlaceTransition resolvePlaceTransition(int previous, int requested, const int32 *globals) {
 PlaceTransition r = {requested,globals[57],false,0};
 static const int gates[][2] = {{307,414},{271,298},{284,289},{324,329},{101,110},
  {120,144},{177,182},{139,151},{160,168}};
 bool gate = false;
 for (const auto &pair : gates) if (previous == pair[0] && requested == pair[1]) gate = true;
 if (gate) {
  if (r.permit == 1) r.permit = 0;
  else r.destination = 429;
 } else if (previous == 208 || previous == 387) r.permit = 0;
 if (previous < 501 || previous > 599 || requested == 408 || requested == 409) {
  if (requested != 513 && requested >= 501 && requested <= 599 && !globals[29]) {
   r.destination = previous; r.immediateSound = 910;
  }
  return r;
 }
 static const int success[] = {20,21,21,21,22,23,24,24,25,26,27,28,29,30,31,
  32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,23,23,23,23,23,31,36};
 if (previous > 537 || globals[success[previous-501]]) return r;
 if (previous >= 502 && previous <= 504 && requested >= 502 && requested <= 504) return r;
 // Original reversed bounds (<=535 || >=531) suppress the voice for this group.
 if (previous == 506 || (previous >= 531 && previous <= 535)) return r;
 if ((previous == 507 || previous == 508) && (requested == 507 || requested == 508)) return r;
 if ((previous == 515 || previous == 536) && requested == 536) return r;
 if ((previous == 520 || previous == 537) && (requested == 520 || requested == 537)) return r;
 r.failureVoice = true;
 return r;
}
}
#endif
