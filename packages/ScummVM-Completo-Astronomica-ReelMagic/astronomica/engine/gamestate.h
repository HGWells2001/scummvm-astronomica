// SPDX-License-Identifier: GPL-3.0-or-later
// Original custom26, ASTRO.EXE4:5a91-6310. See probe_game_state.py.
#ifndef ASTRONOMICA_GAMESTATE_H
#define ASTRONOMICA_GAMESTATE_H
#include "common/scummsys.h"
namespace Astronomica {
struct GameStateContext {
 int32 completed;
 bool resume, helpRunning;
 int32 availableBytes;
};
inline int gameStateGlobal(int key, int selector) {
 if (key == 2 || key == 3) return 50+key;
 if (key == 4 && selector >= 1 && selector <= 27) return 19+selector;
 if (key >= 5 && key <= 11) return 50+key;
 return -1;
}
inline int32 gameStateExternalValue(int key, const GameStateContext &context) {
 if (key == 1) return context.completed;
 if (key == 12) return 1;
 if (key == 13) return context.resume;
 // Preserve original 32-bit addition before the signed comparison.
 const int32 withHelp = int32(uint32(context.availableBytes)+750000U);
 return context.availableBytes > 2400000 || (context.helpRunning && withHelp > 2400000);
}
}
#endif
