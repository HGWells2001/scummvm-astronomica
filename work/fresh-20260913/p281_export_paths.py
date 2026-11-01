"""Explicit source/evidence paths for the P281 gateway revision."""
def paths():
    result=['work/fresh-20260913/'+n for n in ('p281_integration_gate.py','p281_evidence_gate.py','check_p281_gateway.py','check_frozen_p512_v29.py','check_p281_regressions.py','finish_p281_gateway.py','p281_export_paths.py')]
    result+=['outputs/astronomica-cleanroom/evidence/'+n for n in ('p281-gateway-validation.json','p281-source-integration.json','p281-source-review.json')]
    result+=['outputs/astronomica-cleanroom/evidence/p281-native/'+n for n in ('gateway-proof.json','gateway.log')]
    result+=['outputs/astronomica-cleanroom/evidence/p281-frozen-v29/'+n for n in ['frozen-v29-proof.json',*['slot%d-%s.log'%(slot,entry) for slot in (28,29,30) for entry in ('true','false')]]]
    from pathlib import Path
    import json
    integration=Path(__file__).resolve().parent/'p281-integration.json'
    if integration.exists() and 'clock_revision' in json.loads(integration.read_text()):
        result+=['work/fresh-20260913/p512_clock_revision.py','outputs/astronomica-cleanroom/evidence/p281-stopclock-source-review.json']
    return result
