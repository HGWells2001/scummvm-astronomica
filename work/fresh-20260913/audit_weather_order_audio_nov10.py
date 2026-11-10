"""Tie both real-media observations to the exact shipping/baseline sources."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from weather_order_audio_source_nov10 import inject
w=Path(__file__).resolve().parent;r=w.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
shipping=read(w/'weather-order-fix-nov10-stage/proof.json');old=read(w/'builder-mask-guard-seal-nov9-status.json');canonical=r/'outputs/astronomica-cleanroom/engine/astronomica'
results={}
for fixed in(False,True):
 stage=w/('weather-order-audio-fixed-nov10-stage'if fixed else'weather-order-audio-baseline-nov10-stage');build=read(stage/'proof.json');native=read(stage/'native-run/proof.json')
 assert sha(stage/'bin/scummvm.exe')==build['candidate_exe_sha256']==native['candidate_exe_sha256']
 expected=shipping['candidate_engine_sha256']if fixed else old['engine_sha256'];src=stage/'source/engines/astronomica'
 for n,h in expected.items():
  if n!='astronomica.cpp':assert sha(src/n)==h
 assert(src/'astronomica.cpp').read_text()==inject((canonical/'astronomica.cpp').read_text())
 assert native['actual_original_movie_active']and native['decoder_resumed']and native['actual_blocking_sound']==10
 assert native['observed_result_at_voice']==int(fixed) and native['final_result']==0
 results['fixed'if fixed else'baseline']=dict(build_proof_sha256=sha(stage/'proof.json'),native_proof_sha256=sha(stage/'native-run/proof.json'),candidate_exe_sha256=build['candidate_exe_sha256'],script_sha256=sha(src/'script.cpp'),observed_result_at_voice=native['observed_result_at_voice'])
assert results['fixed']['script_sha256']==shipping['candidate_engine_sha256']['script.cpp']and results['baseline']['script_sha256']==old['engine_sha256']['script.cpp']
j=dict(status='REAL_WEATHER_MOVIE_AUDIO_BEFORE_AFTER_SOURCE_CLOSURE_PASS',verified_at=datetime.now(timezone.utc).isoformat(),author_sha256=sha(Path(__file__)),source_injector_sha256=sha(w/'weather_order_audio_source_nov10.py'),shipping_exe_sha256=shipping['candidate_exe_sha256'],results=results,main_unchanged=True,limits=['Only private diagnostic method and voice logging added to ASTRO; full shipping ScriptRunner source exactly matched','Actual original movie and WAV; prior accepted result is a controlled input, not a complete natural UI-history proof'])
(w/'weather-order-audio-review-nov10.json').write_text(json.dumps(j,indent=2)+'\n');print('Actual weather media before/after/source closure PASS')
