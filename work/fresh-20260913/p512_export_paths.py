"""Explicit source/evidence allowlist; no media,binaries or physical saves."""
def paths():
    result=['outputs/astronomica-cleanroom/P512-SAVE-FORMAT.md']
    result+=['work/fresh-20260913/'+n for n in ('check_p512_saves.py','check_p512_regressions.py','check_frozen_p510_v28.py','finish_p512_saves.py','verify_p512_checkpoint.py','p512_integration_gate.py','p512_evidence_gate.py','p512_export_paths.py')]
    result+=['outputs/astronomica-cleanroom/evidence/'+n for n in ('p512-saves-validation.json','p512-save-proof.json','p512-source-integration.json','p512-source-review.json','p512-isolated-normal-proof.json')]
    logs=['ordinary.log','fresh-true.log','fresh-false.log','listed.log','legacy.log','all-normal.log']
    logs+=['fresh-final-%d-%s.log'%(slot,entry) for slot in (29,30) for entry in ('true','false')]
    result+=['outputs/astronomica-cleanroom/evidence/p512-native/'+n for n in logs]
    result+=['outputs/astronomica-cleanroom/evidence/p512-frozen-v28/'+n for n in ['frozen-v28-proof.json',*[kind+'-'+entry+'.log' for kind in ('frozen-slot27','frozen-ordinary-slot27') for entry in ('true','false')]]]
    return result
