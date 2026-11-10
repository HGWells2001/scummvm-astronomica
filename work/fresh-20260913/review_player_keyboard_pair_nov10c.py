"""Bind both freshly audited actual handlers to the causal native counterexample."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=read(w/'motion-geometry-cache-seal-nov10b-status.json');b=read(w/'player-keyboard-baseline-source-review-nov10c.json');g=read(w/'player-keyboard-source-review-nov10c.json');native=read(w/'player-keyboard-native-nov10c/proof.json')
assert b['status'].endswith('PASS')and g['status'].endswith('PASS')and native['status'].endswith('PASS')
assert native['baseline_exe_sha256']==b['candidate_exe_sha256']and native['candidate_exe_sha256']==g['candidate_exe_sha256']
for variant,audit in [('baseline',b),('guard',g)]:
 stage=w/('player-keyboard-baseline-nov10b-stage'if variant=='baseline'else'player-keyboard-guard-nov10c-stage');build=read(stage/'proof.json')
 assert sha(stage/'bin/scummvm.exe')==audit['candidate_exe_sha256']and build['base_exe_sha256']==before['exe_sha256']
 assert audit['archive_members_checked']==7 and audit['verified_reused_framework_objects']==403
 assert audit['engine_class_layout_unchanged']and audit['save_layouts_unchanged']
names=['player-keyboard-baseline-source-review-nov10c.json','player-keyboard-source-review-nov10c.json','player-keyboard-native-nov10c/proof.json']
j=dict(status='PLAYER_KEYBOARD_BASELINE_GUARD_CAUSAL_PAIR_PASS',verified_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=g['candidate_exe_sha256'],baseline_exe_sha256=b['candidate_exe_sha256'],previous_main_exe_sha256=before['exe_sha256'],both_archive_closures_verified=True,both_source_transforms_verified=True,evidence_sha256={n:sha(w/n)for n in names},limits=['Baseline preserves the previous native key switch and adds only a private dispatch/test path','Counterexample is the previous cleanroom engine behavior,not original Windows behavior','No whole-game completeness inference'])
(w/'player-keyboard-pair-review-nov10c.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
