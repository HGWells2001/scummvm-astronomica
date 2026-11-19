// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef ASTRONOMICA_PLOT_H
#define ASTRONOMICA_PLOT_H
#include "common/scummsys.h"
namespace Astronomica {
// P510 custom23 and _qt_callme, independently traced from ASTRO.EXE segment4.
// Times are original movie units at 30Hz, not wall-clock milliseconds.
struct PlotStep {
 int x = -1, y = -1;
 int start = -1, duration = 0, event = 0, time = 0;
 bool play = false, leave = false, success = false;
};
inline PlotStep plotStart(int mode) {
 PlotStep s;
 if (mode < 1 || mode > 3) return s;
 const int starts[] = {0,1800,900}, xs[] = {52,11,108}, ys[] = {257,208,230};
 s.x = xs[mode-1]; s.y = ys[mode-1]; s.start = starts[mode-1];
 s.duration = 359; s.event = 19+mode; s.time = s.start+358;
 return s;
}
inline PlotStep plotCallback(int event, int choice) {
 PlotStep s;
 if (event == 25 || event == 54) { s.leave = true; s.success = event == 54; return s; }
 if (event >= 20 && event <= 32) {
  struct Node { int x,y,start,low,high; };
  static const Node nodes[] = {
   {52,257,0,41,42}, {11,208,1800,43,44}, {108,230,900,44,47},
   {33,143,5400,49,48}, {69,182,2700,43,47}, {0,0,0,0,0},
   {109,153,4500,48,50}, {156,161,3600,46,50}, {77,127,6300,49,50},
   {61,89,8100,52,51}, {151,105,7200,52,51}, {118,57,9000,53,53}, {22,54,9900,53,53}
  };
  const Node &n = nodes[event-20]; s.x = n.x; s.y = n.y; s.play = true;
  if (choice < 1 || choice > 5) return s;
  s.start = n.start + (choice == 3 ? 360 : choice < 3 ? 720 : 540);
  s.duration = choice == 3 ? 90 : 179;
  s.event = choice == 3 ? (event == 31 ? 53 : 25) : choice < 3 ? n.low : n.high;
  // Event30's middle branch uses the last unit instead of end minus three.
  s.time = s.start + s.duration - (event == 30 && choice == 3 ? 1 : 3);
 } else if (event >= 40 && event <= 52 && event != 45) {
  static const int starts[] = {0,1800,900,5400,2700,0,4500,3600,6300,8100,7200,9000,9900};
  s.start = starts[event-40]; s.duration = 359; s.time = s.start+356;
  s.event = event-20; s.play = true;
 } else if (event == 53) {
  s.x = 84; s.y = 21; s.start = 10800; s.duration = 540;
  s.event = 54; s.time = 11337; s.play = true;
 }
 return s;
}
}
#endif
