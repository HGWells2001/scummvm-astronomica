// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef ASTRONOMICA_SCRIPT_H
#define ASTRONOMICA_SCRIPT_H
#include "astronomica/resource.h"
#include "astronomica/gamestate.h"
namespace Astronomica {
// Clock values are milliseconds: original MMSYSTEM ordinal 607, timeGetTime.
class ScriptRunner {
public:
 struct GameStateHandler {
  virtual ~GameStateHandler() {}
  virtual GameStateContext gameStateContext() const = 0;
 };
 void setGameStateHandler(GameStateHandler *handler) { _gameStateHandler = handler; }
 struct SoundHandler {
  virtual ~SoundHandler() {}
  virtual bool isBlockingSound(int id) const = 0;
  virtual uint32 onBlockingSound(int id, uint32 now) = 0;
 };
 void setSoundHandler(SoundHandler *handler) { _soundHandler = handler; }
 void setRocketSupport(bool enabled) { _rocketSupport = enabled; }
 void setEclipseSupport(bool enabled) { _eclipseSupport = enabled; }
 void setPlanetSupport(bool enabled) { _planetSupport = enabled; }
 void setVariantSupport(bool enabled) { _variantSupport = enabled; }
 void setWeatherSupport(bool enabled) { _weatherSupport = enabled; }
 void setResumeSupport(bool enabled, bool fromHelp) { _resumeSupport = enabled; _resumeFromHelp = fromHelp; }
 void setPhotonSupport(bool enabled) { _photonSupport = enabled; }
 void setZodiacSupport(bool enabled) { _zodiacSupport = enabled; }
 void setZodiacRegion(int region) { _zodiacRegion = region; }
 static int photonAnswer(int setting, int scenario);
 void setNoopSuccess(bool enabled) { _noopSuccess = enabled; }
 static int weatherAnswer(int scenario, int a, int b, int c);
 struct BallHandler { virtual ~BallHandler() {} virtual void onBall(int mode, uint32 now) = 0; };
 void setBallHandler(BallHandler *handler) { _ballHandler = handler; }
 struct CometHandler { virtual ~CometHandler() {} virtual void onComet(int mode, uint32 now) = 0; };
 void setCometHandler(CometHandler *handler) { _cometHandler = handler; }
 void setDangerSupport(bool enabled) { _dangerSupport = enabled; }
 void setWorldMovieSupport(bool enabled) { _worldMovieSupport = enabled; }
 bool worldMovieSupport() const { return _worldMovieSupport; }
 void setNativePaletteSupport(bool enabled) { _nativePaletteSupport = enabled; }
 void setAdviceSupport(bool enabled,int previous) { _adviceSupport = enabled; _mentorPrevious = previous; }
 void setMentorSupport(bool enabled, int previous) { _mentorSupport = enabled; _mentorPrevious = previous; }
 void setPlotSupport(bool enabled) { _plotSupport = enabled; }
 void setJupiterSupport(bool enabled) { _jupiterSupport = enabled; }
 void blockClicks() { _clicksBlocked = true; }
 struct ProbeHandler { virtual ~ProbeHandler() {} virtual void onProbe(int mode, int id) = 0; };
 void setProbeHandler(ProbeHandler *handler) { _probeHandler = handler; }
 struct OrbitHandler { virtual ~OrbitHandler() {} virtual bool onOrbitAnswer(int scenario, int choice, uint32 now) = 0; };
 void setOrbitHandler(OrbitHandler *handler) { _orbitHandler = handler; }
 struct RendezvousHandler { virtual ~RendezvousHandler() {} virtual bool onRendezvous(int mode, int speed, uint32 now) = 0; };
 void setRendezvousHandler(RendezvousHandler *handler) { _rendezvousHandler = handler; }
 uint variantRound() const { return _variantRound; }
 void resetVariantSequence() { _variantRound = _variantMask = 0; }
 struct SuccessHandler { virtual ~SuccessHandler() {} virtual uint32 onPuzzleSuccess(uint32 now) = 0; };
 static int successGlobalForPlace(int place);
 void setSuccessHandler(SuccessHandler *handler, int place) { _successHandler = handler; _successGlobal = successGlobalForPlace(place); _successExtraGlobal = place == 529 ? 60 : -1; }
 struct Action { int32 opcode, value, x, y; Common::String text; int32 motion[3] = {}; };
 ScriptRunner() : _lastTrue(false), _clicksBlocked(false), _executed(0), _randomState(1) { memset(_widths, 0, sizeof(_widths)); memset(_known, 0, sizeof(_known)); memset(_values, 0, sizeof(_values)); }
 void loadLocalConditions(const Common::Array<Condition> &conditions);
 void resetGlobals();
 void seedRandom(uint16 seed) { _randomState = seed; }
 uint16 random15();
 void setPrograms(const Common::Array<Script> &scripts, uint32 loadedAt = 0) { _programs = scripts; _programLoadedAt = loadedAt; }
 void setMovieTargets(const Common::Array<uint32> &durations) { _movieDurations = durations; }
 void setImageTargets(const Common::Array<Common::String> &targets) { _imageTargets = targets; }
 void setSoundTargets(const Common::Array<bool> &targets) { _soundTargets = targets; }
 void setSpriteTargets(const Common::Array<uint> &targets) { _spriteTargets = targets; }
 bool defineValue(int scope, int id, int32 value);
 bool getValue(int scope, int id, int32 &value) const;
 bool clicksBlocked() const { return _clicksBlocked; }
 bool canRun(const Script &script, bool timed = false) const { return supports(script, timed) && ready(script, timed); }
 uint executedCount() const { return _executed; }
 bool start(const Script &script, uint32 now, bool allowTimed = false);
 bool enqueue(const Script &script, uint32 now, bool allowTimed = false);
 uint enqueueStartup(const Common::Array<Script> &scripts, uint32 now, bool allowTimed = false);
 void tick(uint32 now);
 void clear() { _pending.clear(); _actions.clear(); }
 void cancelPending() { _pending.clear(); ++_pendingEpoch; }
 bool popAction(Action &action);
 void setLegacyResumeSupport(bool value) { _legacyResumeSupport = value; }
 void setHelpSupport(bool value) { _helpSupport = value; }
 uint pendingCount() const { return _pending.size(); }
 // A settled snapshot contains data only. Programs and callbacks are rebuilt
 // from the original scene; queued work must never be silently discarded.
 enum { kIdleStateWords = 603, kPersistentStateWords = 605 };
 bool scriptsIdle() const { return _pending.empty() && _actions.empty() && !_clicksBlocked; }
 bool exportProbePollState(Common::Array<uint32> &words, uint32 &since) const;
 bool importProbePollState(const Common::Array<uint32> &words, uint32 since);
 bool verifyProbePollSnapshots() const;
 void setP509PendingSupport(bool value) { _p509PendingSupport = value; }
 bool exportP509PendingState(Common::Array<uint32> &words, uint32 now) const;
 bool importP509PendingState(const Common::Array<uint32> &words, uint32 now);
 bool verifyP509PendingSnapshots(const ScriptRunner &recipient, uint32 now) const;
 void setP504PollSupport(bool value) { _p504PollSupport=value; }
 bool exportP504PollState(Common::Array<uint32>&words,uint32 now) const;
 bool importP504PollState(const Common::Array<uint32>&words,uint32 now);
 bool verifyP504PollSnapshots() const;
 void auditP509Snapshot(Common::Array<uint32> &values, Common::Array<uint32> &queue) const;
 uint32 probeDiagnosticHash(bool strict) const;
 bool exportPersistentState(Common::Array<uint32> &words) const;
 bool importPersistentState(const Common::Array<uint32> &words);
 static bool validPersistentState(const Common::Array<uint32> &words) { return validVariantState(words); }
 bool idle() const { return _pending.empty() && _actions.empty() && !_clicksBlocked && !_variantRound; }
 bool exportIdleState(Common::Array<uint32> &words) const;
 static bool validIdleState(const Common::Array<uint32> &words);
 bool importIdleState(const Common::Array<uint32> &words);
 // custom17 keeps two process statics even between idle scene scripts.
 // Older save formats deliberately retain their stricter idle contract.
 bool variantIdle() const { return _variantSupport && _pending.empty() && _actions.empty() && !_clicksBlocked; }
 bool exportVariantState(Common::Array<uint32> &words) const;
 static bool validVariantState(const Common::Array<uint32> &words);
 bool importVariantState(const Common::Array<uint32> &words);
 static bool supports(const Script &script, bool allowTimed = false);
private:
 bool _p504PollSupport=false;
 bool trustedP504PollProgram() const;
 bool validP504PollValues(const Common::Array<uint32>&words,uint32 now) const;
 bool _p509PendingSupport=false;
 bool trustedP509Program() const;
 bool validP509PendingValues(const Common::Array<uint32> &words, uint32 now) const;
 bool trustedProbePollProgram() const;
 void exportSettledValues(Common::Array<uint32> &words) const;
 void importSettledValues(const Common::Array<uint32> &words);
 struct Pending { Script script; uint index; uint32 since; };
 Common::Array<Script> _programs;
 uint32 _programLoadedAt = 0;
 Common::Array<Pending> _pending;
 uint _pendingEpoch = 0;
 BallHandler *_ballHandler = nullptr;
 CometHandler *_cometHandler = nullptr;
 bool _nativePaletteSupport = false;
 bool _jupiterSupport = false, _plotSupport = false, _dangerSupport = false;
 ProbeHandler *_probeHandler = nullptr;
 RendezvousHandler *_rendezvousHandler = nullptr;
 Common::Array<Action> _actions;
 Common::Array<uint> _spriteTargets;
 Common::Array<bool> _soundTargets;
 Common::Array<uint32> _movieDurations;
 Common::Array<Common::String> _imageTargets;
 int32 _values[2][100];
 int32 _widths[2][100];
 bool _known[2][100];
 bool _lastTrue;
 bool _clicksBlocked;
 uint _executed;
 uint32 _randomState;
 GameStateHandler *_gameStateHandler = nullptr;
 SoundHandler *_soundHandler = nullptr;
 OrbitHandler *_orbitHandler = nullptr;
 SuccessHandler *_successHandler = nullptr;
 int _successGlobal = -1;
 int _successExtraGlobal = -1;
 bool _rocketSupport = false;
 bool _eclipseSupport = false;
 bool _planetSupport = false;
 bool _variantSupport = false;
 bool _weatherSupport = false;
 bool _mentorSupport = false, _adviceSupport = false;
 int _mentorPrevious = 0;
 bool _worldMovieSupport = false, _helpSupport = false, _legacyResumeSupport = false;
 bool _resumeSupport = false, _resumeFromHelp = false;
 bool _photonSupport = false;
 bool _zodiacSupport = false;
 int _zodiacRegion = 0;
 bool _noopSuccess = false;
 uint _variantRound = 0, _variantMask = 0; // Original process statics DS:014b/014f.
 bool ready(const Script &script, bool allowTimed) const;
 void execute(const Script &script, uint index, uint32 now);
};
bool verifyScriptRunner();
bool verifyConditions();
}
#endif
