// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef ASTRONOMICA_DANGER_H
#define ASTRONOMICA_DANGER_H
#include "common/array.h"
#include "common/util.h"
namespace Astronomica {
enum DangerOp { kDangerRange, kDangerCallback, kDangerShow, kDangerHide, kDangerHideAll, kDangerPlay, kDangerStop, kDangerSuccess };
struct DangerAction { DangerOp op; int a = 0, b = 0, c = 0; };
struct DangerStep { Common::Array<DangerAction> actions; int destination = 0; };
// Original segment4 _qt_callme call sequences; see p523-callbacks.json.
inline DangerStep dangerCallback(int event, const int channels[3], int buttons, bool solved) {
 DangerStep result; int branch = 0;
 const bool good = event == 1 ? channels[2] >= 75 : event == 4 || event == 10 ? channels[1] >= 75 : event == 6 ? channels[0] >= 40 && channels[1] >= 20 : event == 8 && channels[2] >= 30;
 if (event == 1 || event == 4 || event == 6 || event == 8 || event == 10) branch = good && (buttons & 1) ? 1 : good && (buttons & 2) ? 2 : 0;
 if (event == 18) branch = channels[1] < 60;
 switch (event*3+branch) {
 case 3: { // event1, branch0
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerShow,23});
  result.actions.push_back({kDangerShow,24});
  result.actions.push_back({kDangerRange,602,111});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerCallback,0,3,708});
  break;
 }
 case 4: { // event1, branch1
  result.actions.push_back({kDangerRange,721,100});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerCallback,0,2,818});
  break;
 }
 case 5: { // event1, branch2
  result.actions.push_back({kDangerRange,841,120});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerCallback,0,2,958});
  break;
 }
 case 6: { // event2, branch0
  result.actions.push_back({kDangerRange,961,602});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerCallback,0,4,1560});
  result.actions.push_back({kDangerCallback,1,14,1470});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerShow,7});
  result.actions.push_back({kDangerHide,5});
  result.actions.push_back({kDangerHide,6});
  result.actions.push_back({kDangerHide,1});
  result.actions.push_back({kDangerShow,17});
  result.actions.push_back({kDangerShow,9});
  break;
 }
 case 9: { // event3, branch0
  result.actions.push_back({kDangerStop});
  result.destination = 117;
  break;
 }
 case 12: { // event4, branch0
  result.actions.push_back({kDangerRange,1561,100});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerShow,34});
  result.actions.push_back({kDangerShow,35});
  result.actions.push_back({kDangerShow,36});
  result.actions.push_back({kDangerShow,37});
  result.actions.push_back({kDangerCallback,0,3,1658});
  break;
 }
 case 13: { // event4, branch1
  result.actions.push_back({kDangerRange,1681,220});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerCallback,0,5,1898});
  break;
 }
 case 14: { // event4, branch2
  result.actions.push_back({kDangerRange,1921,240});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerCallback,0,5,2158});
  break;
 }
 case 15: { // event5, branch0
  result.actions.push_back({kDangerRange,2160,601});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerCallback,0,6,2758});
  result.actions.push_back({kDangerCallback,1,15,2670});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerShow,7});
  result.actions.push_back({kDangerHide,5});
  result.actions.push_back({kDangerHide,6});
  result.actions.push_back({kDangerHide,1});
  result.actions.push_back({kDangerShow,13});
  result.actions.push_back({kDangerShow,26});
  break;
 }
 case 18: { // event6, branch0
  result.actions.push_back({kDangerRange,2761,80});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerCallback,0,3,2838});
  break;
 }
 case 19: { // event6, branch1
  result.actions.push_back({kDangerRange,2881,120});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerCallback,0,7,2998});
  break;
 }
 case 20: { // event6, branch2
  result.actions.push_back({kDangerRange,3001,120});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerCallback,0,7,3118});
  break;
 }
 case 21: { // event7, branch0
  result.actions.push_back({kDangerRange,3121,601});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerCallback,0,8,3718});
  result.actions.push_back({kDangerCallback,1,16,3630});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerShow,7});
  result.actions.push_back({kDangerHide,5});
  result.actions.push_back({kDangerHide,6});
  result.actions.push_back({kDangerHide,1});
  result.actions.push_back({kDangerShow,12});
  break;
 }
 case 24: { // event8, branch0
  result.actions.push_back({kDangerShow,25});
  // Original 4:7a87-7a9f pushes WORDs instead of DWORDs.
  // Restore the explicit 3721/80 range; the original duration is uninitialized.
  result.actions.push_back({kDangerRange,3721,80});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerCallback,0,3,3798});
  break;
 }
 case 25: { // event8, branch1
  result.actions.push_back({kDangerRange,3841,100});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerCallback,0,9,3938});
  break;
 }
 case 26: { // event8, branch2
  result.actions.push_back({kDangerRange,3961,120});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerCallback,0,9,4078});
  break;
 }
 case 27: { // event9, branch0
  result.actions.push_back({kDangerRange,4080,601});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerCallback,0,10,4678});
  result.actions.push_back({kDangerCallback,1,17,4590});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerShow,7});
  result.actions.push_back({kDangerHide,5});
  result.actions.push_back({kDangerHide,6});
  result.actions.push_back({kDangerHide,1});
  result.actions.push_back({kDangerShow,10});
  result.actions.push_back({kDangerShow,21});
  break;
 }
 case 30: { // event10, branch0
  result.actions.push_back({kDangerRange,4681,80});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerShow,34});
  result.actions.push_back({kDangerShow,35});
  result.actions.push_back({kDangerShow,36});
  result.actions.push_back({kDangerShow,37});
  result.actions.push_back({kDangerCallback,0,3,4758});
  break;
 }
 case 31: { // event10, branch1
  result.actions.push_back({kDangerRange,4801,100});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerCallback,0,11,4898});
  break;
 }
 case 32: { // event10, branch2
  result.actions.push_back({kDangerRange,4921,120});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerCallback,0,11,5038});
  break;
 }
 case 33: { // event11, branch0
  result.actions.push_back({kDangerRange,5040,641});
  result.actions.push_back({kDangerPlay});
  result.actions.push_back({kDangerCallback,0,12,5678});
  result.actions.push_back({kDangerCallback,1,18,5540});
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerShow,7});
  result.actions.push_back({kDangerHide,5});
  result.actions.push_back({kDangerHide,6});
  result.actions.push_back({kDangerHide,1});
  result.actions.push_back({kDangerShow,14});
  result.actions.push_back({kDangerShow,20});
  break;
 }
 case 36: { // event12, branch0
  result.actions.push_back({kDangerStop});
  if (!solved) result.actions.push_back({kDangerSuccess});
  result.destination = 524;
  break;
 }
 case 39: { // event13, branch0
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerShow,5});
  result.actions.push_back({kDangerShow,6});
  result.actions.push_back({kDangerHide,7});
  result.actions.push_back({kDangerShow,1});
  break;
 }
 case 42: { // event14, branch0
  result.actions.push_back({kDangerShow,5});
  result.actions.push_back({kDangerShow,6});
  result.actions.push_back({kDangerShow,1});
  result.actions.push_back({kDangerHide,7});
  break;
 }
 case 45: { // event15, branch0
  result.actions.push_back({kDangerShow,5});
  result.actions.push_back({kDangerShow,6});
  result.actions.push_back({kDangerShow,1});
  result.actions.push_back({kDangerHide,7});
  break;
 }
 case 48: { // event16, branch0
  result.actions.push_back({kDangerShow,5});
  result.actions.push_back({kDangerShow,6});
  result.actions.push_back({kDangerShow,1});
  result.actions.push_back({kDangerHide,7});
  break;
 }
 case 51: { // event17, branch0
  result.actions.push_back({kDangerShow,5});
  result.actions.push_back({kDangerShow,6});
  result.actions.push_back({kDangerShow,1});
  result.actions.push_back({kDangerHide,7});
  break;
 }
 case 55: { // event18, branch1
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerShow,5});
  result.actions.push_back({kDangerShow,6});
  result.actions.push_back({kDangerShow,1});
  result.actions.push_back({kDangerHide,7});
  result.actions.push_back({kDangerShow,31});
  result.actions.push_back({kDangerShow,32});
  result.actions.push_back({kDangerShow,33});
  result.actions.push_back({kDangerCallback,1,19,5610});
  break;
 }
 case 54: { // event18, branch0
  result.actions.push_back({kDangerHideAll});
  result.actions.push_back({kDangerShow,5});
  result.actions.push_back({kDangerShow,6});
  result.actions.push_back({kDangerShow,1});
  result.actions.push_back({kDangerHide,7});
  break;
 }
 case 57: { // event19, branch0
  result.actions.push_back({kDangerShow,27});
  result.actions.push_back({kDangerShow,28});
  result.actions.push_back({kDangerShow,29});
  result.actions.push_back({kDangerShow,30});
  break;
 }
 default: break;
 }
 return result;
}
inline int dangerControlY(int value) {
 // Exact evaluation of the original stored binary64 constant in x87.
 // All intermediates fit its64-bit significand. Binary64 subtraction
 // would incorrectly round values20/40/60/80 onto an integer boundary.
 return int((int64(414)*INT64_C(4503599627370496)-int64(value)*INT64_C(2476979795053773))/INT64_C(4503599627370496));
}
inline void dangerAdjust(int channels[3], int button) {
 if (button < 1 || button > 6) return;
 const int order[3][3] = {{0,1,2},{1,0,2},{2,1,0}};
 const int *ids = order[(button-1)%3];
 const float first = float(MAX(0,MIN(99,channels[ids[0]]+(button <= 3 ? -10 : 10))));
 const float b = float(channels[ids[1]]), c = float(channels[ids[2]]);
 const float ratio = b+c < 1 ? 0.5f : float(double(b)/double(b+c));
 const float second = float(double(ratio)*(99.0-double(first)));
 const float third = float(99.0-(double(first)+double(second)));
 channels[ids[0]] = int(first);
 channels[ids[1]] = int(MAX(0.0f,MIN(99.0f,second)));
 channels[ids[2]] = int(MAX(0.0f,MIN(99.0f,third)));
}
}
#endif
