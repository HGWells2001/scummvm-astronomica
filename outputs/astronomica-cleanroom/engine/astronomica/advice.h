// SPDX-License-Identifier: GPL-3.0-or-later
// Original custom27/custom32. Independently checked by probe_p409_*.py.
#ifndef ASTRONOMICA_ADVICE_H
#define ASTRONOMICA_ADVICE_H
#include "common/scummsys.h"
namespace Astronomica {
struct AdviceClip { int start, duration; };
struct AdviceResult { AdviceClip clip; int32 side, stage, flag55, flag56; };
template<class Random>
AdviceResult chooseAdvice(int previous, int32 completed, int32 solved, int32 stage, int32 flag55, int32 flag56, Random draw) {
 AdviceResult r = {{0,0},0,stage,flag55,flag56};
 auto clip = [&](int first,int end) { r.clip = {first-5,end-first+20}; };
 if (solved == 1) clip(0x15d8,0x1782);
 else if (previous == 208 && completed <= 1) clip(0xfbd,0x11a0);
 else if (completed >= 9 && stage == 0) { clip(0x121b,0x137a); r.stage = 1; }
 else if (completed >= 22 && stage == 1) { clip(0x13f2,0x155d); r.stage = 2; }
 else if (completed >= 26 && stage == 2) { clip(0x15d8,0x1782); r.stage = 3; }
 else if (flag56 == 1) { clip(0x40bc,0x4471); r.side = 1; r.flag56 = 0; }
 else if (flag55 == 1) { clip(0x35ac,0x3930); r.side = 1; r.flag55 = 0; }
 else {
  r.side = draw(0,1);
  if (!r.side) {
   static const AdviceClip clips[] = {{118,239},{442,236},{778,227},{1105,197},{1405,200},{1708,197},{2005,236},{2341,233},{2677,227},{3004,242},{3349,223},{3685,239},{6133,227}};
   r.clip = clips[draw(1,13)-1];
  } else {
   // Original makes an extra draw: group1 versus groups2/3/4.
   const int group = draw(1,4), selection = draw(1,4);
   static const AdviceClip clips[] = {{6583,713},{7339,581},{7963,345},{8350,785},{9178,1375},{10594,1275},{11971,1575},{14686,1355}};
   r.clip = clips[(group == 1 ? 0 : 4)+selection-1];
  }
 }
 return r;
}
inline bool adviceStartsClock(int32 solved, uint32 previous) { return solved == 1 && previous == 0; }
}
#endif

