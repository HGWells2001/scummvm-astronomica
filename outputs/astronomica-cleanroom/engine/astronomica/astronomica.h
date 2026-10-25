// SPDX-License-Identifier: GPL-3.0-or-later
// Fresh reverse engineering of D:/astro, 2026-09-13.
#ifndef ASTRONOMICA_ASTRONOMICA_H
#define ASTRONOMICA_ASTRONOMICA_H
#include "engines/engine.h"
#include "audio/mixer.h"
namespace Video { class QuickTimeDecoder; }
namespace Audio { class SeekableAudioStream; }
#include "graphics/surface.h"
#include "astronomica/resource.h"
#include "astronomica/help.h"
#include "astronomica/legacy_save.h"
#include "astronomica/script.h"
#include "astronomica/sprites.h"
#include "astronomica/plot.h"
#include "astronomica/danger.h"
#include "astronomica/transitions.h"
namespace Astronomica {
class AstronomicaEngine : public Engine, public ScriptRunner::GameStateHandler, public ScriptRunner::SuccessHandler, public ScriptRunner::SoundHandler, public ScriptRunner::OrbitHandler, public ScriptRunner::RendezvousHandler, public ScriptRunner::ProbeHandler, public ScriptRunner::BallHandler, public ScriptRunner::CometHandler {
public:
 explicit AstronomicaEngine(OSystem *system) : Engine(system), _place(-1), _previousPlace(-1) { _nav[0] = _nav[1] = _nav[2] = 0; }
 ~AstronomicaEngine() override;
 Common::Error run() override;
 bool hasFeature(EngineFeature f) const override { return f == kSupportsSavingDuringRuntime || f == kSupportsLoadingDuringRuntime; }
 bool canSaveGameStateCurrently(Common::U32String *msg = nullptr) override;
 bool canLoadGameStateCurrently(Common::U32String *msg = nullptr) override;
 Common::Error saveGameStream(Common::WriteStream *stream, bool isAutosave = false) override;
 Common::Error loadGameStream(Common::SeekableReadStream *stream) override;
private:
 LegacySaveState _legacyState;
 bool _legacyChecked = false, _legacyAvailable = false;
 void prepareLegacyResume();
 bool validateLegacyDestination(const LegacySaveState &state) const;
 bool restoreLegacyState(const LegacySaveState &state);
 bool verifyLegacySaves();
 HelpBook _helpBook;
 bool _helpAttempted = false;
 uint _helpOpened = 0;
 bool ensureHelpBook();
 void openHelpBook();
 bool verifyHelp();
 struct HoverTarget { int width = 0, height = 0; bool ready = false, entered = false; };
 Common::Array<HoverTarget> _hoverSprites, _hoverRects;
 void configureHover();
 void hoverAtTime(int x, int y, uint32 now);
 bool verifyHover();
 bool verifyWorldMovie29();
 bool verifyWorldMovies(bool continuous);
 bool verifyIntro();
 bool verifyLogo(bool actualExit);
 bool verifyPostCredits();
 bool verifyEndings();
 bool verifyAdvice();
 void updateWorldAt(uint32 now);
 bool verifySaves();
 bool canSaveQuestion() const;
 Common::Error saveQuestion(Common::WriteStream *stream);
 Common::Error loadQuestion(Common::SeekableReadStream *stream, uint32 version);
 bool verifyP508Saves();
 bool verifyP505Saves();
 bool canSaveP519() const;
 Common::Error saveP519(Common::WriteStream *stream);
 Common::Error loadP519(Common::SeekableReadStream *stream);
 bool verifyP519Saves();
 bool canSaveP524() const;
 Common::Error saveP524(Common::WriteStream *stream);
 Common::Error loadP524(Common::SeekableReadStream *stream);
 bool verifyP524Saves();
 bool canSaveP526() const;
 Common::Error saveP526(Common::WriteStream *stream);
 Common::Error loadP526(Common::SeekableReadStream *stream);
 bool verifyP526Saves();
 bool verifyPresentation();
 bool verifyAudioChannels();
 bool canSaveP528() const;
 Common::Error saveP528(Common::WriteStream *stream);
 Common::Error loadP528(Common::SeekableReadStream *stream);
 bool verifyP528Saves();
 bool canSaveP530() const;
 Common::Error saveP530(Common::WriteStream *stream);
 Common::Error loadP530(Common::SeekableReadStream *stream);
 bool verifyP530Saves();
 bool canSaveVariant() const;
 Common::Error saveVariant(Common::WriteStream *stream);
 Common::Error loadVariant(Common::SeekableReadStream *stream);
 bool verifyVariantSaves();
 bool verifySaveEntryHistory();
 bool canSaveBuilder() const;
 Common::Error saveBuilder(Common::WriteStream *stream);
 Common::Error loadBuilder(Common::SeekableReadStream *stream);
 bool verifyBuilderSaves();
 bool verifyRocketBoundaries();
 bool canSaveRendezvous() const;
 Common::Error saveRendezvous(Common::WriteStream *stream);
 Common::Error loadRendezvous(Common::SeekableReadStream *stream);
 bool verifyRendezvousSaves();
 bool _rendezvousAssetsValid=false;
 bool canSaveProbe() const;
 Common::Error saveProbe(Common::WriteStream *stream);
 Common::Error loadProbe(Common::SeekableReadStream *stream);
 bool verifyProbeSaves();
 bool _probeAssetsValid = false;
 bool canSaveUniverse() const;
 Common::Error saveUniverse(Common::WriteStream *stream);
 Common::Error loadUniverse(Common::SeekableReadStream *stream);
 bool verifyUniverseSaves();
 bool canSaveRocket() const;
 Common::Error saveRocket(Common::WriteStream *stream);
 Common::Error loadRocket(Common::SeekableReadStream *stream);
 bool verifyRocketSaves();
 bool canSaveP517() const;
 Common::Error saveP517(Common::WriteStream *stream);
 Common::Error loadP517(Common::SeekableReadStream *stream);
 bool verifyP517Saves();
 bool canSaveP513() const;
 Common::Error saveP513(Common::WriteStream *stream);
 Common::Error loadP513(Common::SeekableReadStream *stream);
 bool verifyP513Saves();
 bool verifyGameState();
 GameStateContext gameStateContext() const override {
  // Original text GAMESTAT is admitted only after complete validation.
  // The Win16 free-memory warning has no equivalent in this port.
  return {int32(_puzzlesCompleted),_legacyAvailable,false,3000000};
 }
 void pauseEngineIntern(bool pause) override;
 bool _clockPaused = false;
 uint32 _pauseStarted = 0, _pausedMillis = 0;
 RocketMotion _rocket;
 ProbeMotion _probe;
 BallMotion _ball;
 CometMotion _comet;
 void onComet(int mode, uint32 now) override;
 bool verifyCometPuzzles();
 bool verifyP527Saves();
 bool canSaveP527() const;
 Common::Error saveP527(Common::WriteStream*stream);
 Common::Error loadP527(Common::SeekableReadStream*stream);
 bool _p527AssetsValid=false;
 bool verifyP516Saves();
 bool canSaveP516() const;
 Common::Error saveP516(Common::WriteStream*stream);
 Common::Error loadP516(Common::SeekableReadStream*stream);
 void p516Extra(Common::Array<uint32>&words) const;
 bool _p516AssetsValid=false;
 bool verifyP516Puzzle();
 int _jupiterWidths[8] = {}, _jupiterHeights[8] = {};
 void cycleExplosion(int id, int x, int y, uint32 now);
 void onBall(int mode, uint32 now) override;
 void queueBallCommand(int opcode, int value, int frame, int delay, uint32 now);
 bool verifyP501Puzzle();
 void onProbe(int mode, int id) override;
 bool verifyProbeBoundaries();
 bool verifyP522Puzzle();
 bool verifyP524Puzzle();
 Video::QuickTimeDecoder *_movie = nullptr;
 Graphics::Surface _movieFrame;
 int _moviePresentedFrame = -1;
 uint32 _universeSegmentEnd = 0;
 bool _universeAssetsValid = false;
 bool _moviePlaying = false;
 int _worldMovieCursorBottom = -1;
 int _movieX = 0, _movieY = 0;
 uint32 _movieSegmentStart = 0;
 uint _movieFramesDrawn = 0;
 void closeMovie();
 void configureMovie();
 void updateMovie();
 void applyPlotStep(const PlotStep &step);
 void applyDangerStep(const DangerStep &step);
 void runDangerEvent(int event);
 void dangerCustom(int operation, int mode);
 bool verifyP523Puzzle();
 bool verifyMentors();
 int _dangerChannels[3] = {33,33,33}, _dangerButtons = 0;
 int _dangerEvent[2] = {};
 uint32 _dangerTime[2] = {};
 bool verifyP510Puzzle();
 int _plotEvent = 0;
 uint32 _plotTime = 0;
 int _place;
 int _previousPlace;
 int32 _nav[3];
 Graphics::Surface _screen;
 Graphics::Surface _background;
 Scene _scene;
 Common::Array<Sprite> _questionSaveBaseline;
 ScriptRunner _runner;
 Audio::SoundHandle _soundHandle;
 uint _soundsStarted = 0;
 int _lastSound = -1;
 Audio::SeekableAudioStream *openSound(int id);
 void configureSounds();
 void configureImages();
 Graphics::Surface *openBackgroundImage(const Common::String &name, int place = -1);
 bool stageBackgroundImage(const Common::String &name, int x, int y);
 void displayBackgroundImage();
 Graphics::Surface _pendingImage;
 Common::String _pendingImageName, _displayedImageName;
 uint _p519LargeImage = 0, _p519SmallImage = 0;
 uint _p528EarthImage = 0, _p528MoonImage = 0, _p528TallMoon = 0;
 bool _p528HistoryValid = true;
 bool _p530HistoryValid = true;
 bool _p513HistoryValid = true;
 bool _p517HistoryValid = true;
 bool _builderHistoryValid = true;
 int _pendingImageX = 0, _pendingImageY = 0;
 bool playSound(int id, uint32 now = 0, bool looping = false);
 void resumeLoopAt(uint32 now);
 int _loopSound = -1;
 bool _loopEnabled = true;
 uint32 _lastSoundAt = 0;
 bool verifyAudio();
 bool verifyAuroraPuzzle();
 bool verifySpectrumPuzzle();
 bool verifyMoveFrameCommand();
 bool verifySolarPuzzle();
 bool verifyUniverseBoundaries();
 bool verifyUniversePuzzle();
 bool verifyP530Puzzle();
 bool verifyEclipsePuzzle();
 bool verifyP521Puzzle();
 bool verifyP518Puzzle();
 bool verifyP511Saves();
 bool canSaveP511() const;
 Common::Error saveP511(Common::WriteStream *stream);
 Common::Error loadP511(Common::SeekableReadStream *stream);
 bool _p511AssetsValid=false;
 bool verifyP509Saves();
 bool canSaveP509() const;
 Common::Error saveP509(Common::WriteStream *stream);
 Common::Error loadP509(Common::SeekableReadStream *stream);
 bool _p509AssetsValid=false;
 bool verifyP509BoundaryAudit();
 bool verifyP521Saves();
 bool canSaveP521() const;
 Common::Error saveP521(Common::WriteStream *stream);
 Common::Error loadP521(Common::SeekableReadStream *stream);
 bool _p521AssetsValid=false;
 bool verifyPlanetSaves();
 bool canSavePlanets() const;
 Common::Error savePlanets(Common::WriteStream *stream);
 Common::Error loadPlanets(Common::SeekableReadStream *stream);
 bool _planetAssetsValid=false;
 bool verifyP526Puzzle();
 bool verifyP512Puzzle();
 bool verifyBuilderPuzzle();
 bool verifyP514Puzzle();
 bool verifyP513Puzzle();
 bool verifyP507Wheel();
 bool onRendezvous(int mode, int speed, uint32 now) override;
 bool onOrbitAnswer(int scenario, int choice, uint32 now) override;
 bool verifyVariantPuzzles();
 bool verifyContinuousMovies();
 bool isBlockingSound(int id) const override;
 uint32 onBlockingSound(int id, uint32 now) override;
 uint32 _lastBlockingSoundEnd = 0;
 uint32 onPuzzleSuccess(uint32 now) override;
 uint32 _puzzlesCompleted = 0, _lastSuccessEnd = 0;
 int spriteAt(int x, int y);
 void clickAt(int x, int y);
 void clickAtTime(int x, int y, uint32 now);
 uint32 scriptClock() const;
 void runScripts();
 void runScriptsAt(uint32 now);
 void applyScriptActions(uint32 now);
 void animateSpritesAt(uint32 now);
 void queueEntryScripts();
 void presentScene();
 void redrawSprites();
 bool demoVisibility(bool visible);
 bool demoMovement(int x);
 bool demoOffset(int spriteId = 8);
 bool demoFrame(int frame);
 uint renderStaticSprites(Common::SeekableReadStream &stream, const Scene &scene, Graphics::Surface &target);
 bool changePlace(int place);
 bool verifyTransitions();
 bool loadPlace(int place, bool keepSound = false, bool restoring = false);
 bool readImage(Common::SeekableReadStream &stream, Graphics::Surface &target, bool control);
 void stepPlace(int direction);
};
}
#endif
