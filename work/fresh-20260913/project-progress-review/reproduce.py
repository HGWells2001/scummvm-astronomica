"""Reproduce the fixed ten-gate acceptance index for the verified P504 baseline.

Writes only this review directory. This is a milestone index, not an effort estimate.
Update the explicit verified-baseline input only after a later publication is sealed;
do not change the ten gates or use a pending candidate to replace passed evidence.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json

here=Path(__file__).resolve().parent
root=here.parents[2]
read_root=here/'baseline-evidence' if (here/'baseline-evidence').exists() else root
work=read_root/'work/fresh-20260913'
evidence=read_root/'outputs/astronomica-cleanroom/evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
publication=read(work/'p504-completion-status.json')
checkpoint=read(work/'p504-checkpoint-status.json')
seal=read(work/'p504-seal-status.json')
assert publication['status']==checkpoint['status']==seal['status']=='PASS'
assert checkpoint['full_suite'] and publication['clean_clone'] and publication['remote_verified']
exe=publication['exe_sha256']
assert checkpoint['exe_sha256']==seal['exe_sha256']==exe
assert publication['published_commit']==seal['published_commit']=='1af25c6ced7b315e2c7bbd7bba3c58d125a0c022'
snapshot=Path(seal['verified_snapshot'])
assert sha(snapshot/'scummvm.exe')==exe
development=read(evidence/'development-validation.json')
saves=read(evidence/'native-save-coverage.json')
launcher=read(evidence/'local-launcher-validation.json')
audio=read(evidence/'audio-channels-validation.json')
presentation=read(evidence/'presentation-validation.json')
help_=read(evidence/'help-native-validation.json')
templates=read(evidence/'puzzle-coverage.json')
assert development['exe_sha256']==saves['exe_sha256']==launcher['exe_sha256']==audio['exe_sha256']==presentation['exe_sha256']==exe
assert development['build_exit']==development['runtime_exit']==0
assert len(development['engine_sha256'])==23
assert len(development['complete_route_scenes'])==35
assert launcher['status']=='PASS' and launcher['normal_P1_startup'] and launcher['personal_saves_untouched']
assert audio['status']==presentation['status']=='PASS' and audio['full_suite'] and presentation['full_suite']
assert help_['status']=='PASS' and help_['readable_articles']==help_['rendered_articles']==781 and help_['inline_images']==31
assert saves['supported_puzzle_route_scenes']==30 and saves['inventoried_puzzle_route_scenes']==35

def gate(id,title,status,condition,paths,remaining):
    return dict(id=id,title=title,status=status,weight=1,pass_condition=condition,evidence=paths,remaining=remaining)
gates=[
 gate('A01','Native ScummVM integration and reproducible local build','PASS',
      'The actual Windows x64 ScummVM engine detects the supported original copy, builds against the pinned core, and passes its current same-build execution checks.',
      ['outputs/astronomica-cleanroom/engine/astronomica/detection.cpp','outputs/astronomica-cleanroom/evidence/development-validation.json','work/fresh-20260913/p504-checkpoint-status.json'],[]),
 gate('A02','Ordinary launcher, input and navigation baseline','PASS',
      'Normal P1 startup uses the playable configuration and original input/navigation routes, with personal preferences and saves preserved and diagnostic mode disabled.',
      ['outputs/astronomica-cleanroom/LOCAL-PLAY.md','outputs/astronomica-cleanroom/evidence/local-launcher-validation.json','outputs/astronomica-cleanroom/evidence/runtime.log'],
      ['This gate covers the automated ordinary-start/input baseline; the integrated human UI check is A09.']),
 gate('A03','Exhaustive required original-behavior and branch inventory','UNVERIFIED',
      'A versioned inventory identifies all required game routes and important alternative/failure/time-dependent branches from the original assets, maps each to execution evidence or an explicit accepted limitation, and leaves no required unknown branch.',
      ['outputs/astronomica-cleanroom/evidence/development-validation.json','outputs/astronomica-cleanroom/evidence/puzzle-coverage.json','outputs/astronomica-cleanroom/NEXT-STEPS.md'],
      ['The 35 inventoried route scenes include variants and do not establish an exhaustive whole-game route/branch denominator.',
       '114/121 is static canRun with animation disabled, not executed original behavior; classify those seven rejects without automatically calling them bugs.',
       'No new execution of the original Windows program is implied. Bounded unknowns remain until evidence or a documented scope decision resolves them.']),
 gate('A04','All currently inventoried puzzle route suites','PASS',
      'Every one of the 35 declared puzzle route scenes has passing automated native route checks on the same verified executable.',
      ['outputs/astronomica-cleanroom/evidence/development-validation.json','outputs/astronomica-cleanroom/evidence/runtime.log','work/fresh-20260913/p504-checkpoint-status.json'],
      ['This gate closes the existing automated route inventory; A03 and A09 separately address its coverage limits and integrated play.']),
 gate('A05','Automated audiovisual pipeline and presentation','PASS',
      'The supported original video/WAV pipeline, Music/Effects behavior and full-frame presentation checks pass on the verified executable.',
      ['outputs/astronomica-cleanroom/evidence/audio-channels-validation.json','outputs/astronomica-cleanroom/evidence/presentation-validation.json','outputs/astronomica-cleanroom/evidence/development-validation.json'],
      ['These are automated decoder/state/channel/pixel checks, not a claim of complete manual listening or whole-game audiovisual parity.']),
 gate('A06','Native reference-help content and interaction','PASS',
      'The native help reads and renders all781 original articles and31 original images with working article navigation, scrolling, search and modal return.',
      ['outputs/astronomica-cleanroom/evidence/help-native-validation.json','outputs/astronomica-cleanroom/evidence/help-native-runtime.log'],
      ['Original typography fidelity is deliberately a separate acceptance gate A08.']),
 gate('A07','Useful safe-boundary native saves for the complete puzzle-route inventory','PARTIAL',
      'Exploration and all35 inventoried puzzle-route scenes support documented useful stable-progress save boundaries, with exact successor/fresh-process/metadata tests, malformed-load atomicity and backward compatibility.',
      ['outputs/astronomica-cleanroom/evidence/native-save-coverage.json','outputs/astronomica-cleanroom/P504-SAVE-FORMAT.md'],
      ['Five remaining scene scopes: P501,P510,P512,P523,P525.',
       '30supported scopes retain their explicit exclusions; arbitrary saves during every active voice, transition or pending command are not silently promised.',
       'Current ambient restart convention does not preserve sample cursor; determine whether that convention is acceptable for the fixed release scope.']),
 gate('A08','Reference-help typography and layout fidelity','PARTIAL',
      'Original paragraph/table measurements and required font/superscript presentation are reproduced and checked against original reference images.',
      ['outputs/astronomica-cleanroom/evidence/help-native-validation.json','outputs/astronomica-cleanroom/README.md'],
      ['Exact typography and original paragraph/table measurements remain outstanding.',
       '13 original exponent runs are currently rendered using explicit ^(value) notation rather than faithful original superscript typography.']),
 gate('A09','Integrated manual audiovisual playthrough','UNVERIFIED',
      'A human completes a normal new-game-to-ending playthrough on the supported original copy, checks mouse/UI/audio/video/help/save-resume at representative progress points and records reproducible outcomes; required alternate routes are checked or explicitly scoped.',
      ['outputs/astronomica-cleanroom/LOCAL-PLAY.md','outputs/astronomica-cleanroom/evidence/local-launcher-validation.json','outputs/astronomica-cleanroom/evidence/help-native-validation.json'],
      ['User/manual confirmation is still required; automated component suites cannot mark this gate passed.',
       'Observed issues may reopen the relevant gates.']),
 gate('A10','Regression integrity, compatibility and recoverable source publication','PASS',
      'The same executable completes the full suite, genuine previous-version slots remain compatible, exact source/build hashes are retained, and a clean source-only clone plus remote commit are verified and sealed.',
      ['work/fresh-20260913/p504-checkpoint-status.json','work/fresh-20260913/p504-completion-status.json','work/fresh-20260913/p504-seal-status.json','outputs/astronomica-cleanroom/evidence/development-validation.json'],[]),
]
passed=sum(g['status']=='PASS' for g in gates)
assert len(gates)==10 and passed==6
files={path for g in gates for path in g['evidence']}
result=dict(scheme='astronomica-acceptance-v1',scheme_date='2026-10-27',scheme_status='FORWARD_FIXED_ACCEPTANCE_CHECKLIST',
            observed_at_utc=datetime.now(timezone.utc).isoformat(),verified_baseline=dict(scene=504,format_version=26,exe_sha256=exe,published_commit=publication['published_commit'],snapshot=str(snapshot)),
            overall_acceptance_index=dict(passed=passed,total=10,percent=100*passed/10,calculation='100 * count(PASS) / 10; PARTIAL and UNVERIFIED each count zero',meaning='Fixed milestone acceptance index; not a measured fraction of engineering effort or a guarantee of whole-game playability'),
            whole_game_completion_percent=None,estimated_remaining_effort_percent=None,
            metrics=dict(native_safe_save_scene_coverage=dict(supported=30,total=35,percent=round(100*30/35,1),unsupported=saves['unsupported_puzzle_route_scenes']),
                         static_entry_templates=dict(accepted=templates['accepted'],total=templates['total'],percent=round(100*templates['accepted']/templates['total'],1),meaning=templates['metric']),
                         automated_route_scene_inventory=dict(passed=35,total=35,meaning='Inventoried route scenes include variants; not a count of distinct puzzles or an exhaustive whole-game denominator')),
            evidence_base=str(read_root),gates=gates,evidence_sha256={path:sha(read_root/path) for path in sorted(files)},
            frozen_rules=['Keep exactly these ten gates and binary PASS scoring for future reports; do not split or merge gates to alter the percentage.',
                          'New acceptance requirements require an explicit versioned scheme change, not silent denominator changes.',
                          'A pending candidate does not invalidate the last verified baseline or earn a PASS before its required checks finish.',
                          'Do not overwrite existing official manifests containing whole_game_completion_percent=null with this different index.',
                          'Upstream merge acceptance, additional platforms/editions and distribution packaging are outside this Windows-original-copy target unless separately requested; official ScummVM submission readiness is not established by the private source publication.'])
(here/'acceptance-index.json').write_text(json.dumps(result,indent=2)+'\n')
print('Acceptance v1:',passed,'/10 =',result['overall_acceptance_index']['percent'],'%; save scene coverage30/35=85.7%; engineering-effort/whole-game percentage remains undefined')
