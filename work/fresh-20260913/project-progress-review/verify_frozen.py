"""Read-only validation of the original ten-gate report and frozen inputs."""
from pathlib import Path
import hashlib,json
here=Path(__file__).resolve().parent
j=json.loads((here/'acceptance-index.json').read_text());m=json.loads((here/'baseline-manifest.json').read_text())
assert j['scheme']=='astronomica-acceptance-v1' and len(j['gates'])==10
assert [g['id'] for g in j['gates']]==['A%02d'%i for i in range(1,11)]
assert all(g['weight']==1 and g['pass_condition'] and g['evidence'] for g in j['gates'])
assert sum(g['status']=='PASS' for g in j['gates'])==6
assert j['overall_acceptance_index']['percent']==60.0 and j['whole_game_completion_percent'] is None and j['estimated_remaining_effort_percent'] is None
assert j['evidence_sha256']==m['evidence_sha256']
assert j['verified_baseline']['published_commit']==m['published_commit']=='1af25c6ced7b315e2c7bbd7bba3c58d125a0c022'
for name,expected in m['evidence_sha256'].items():assert hashlib.sha256((here/'baseline-evidence'/name).read_bytes()).hexdigest()==expected,name
print('Frozen acceptance v1 integrity PASS:6/10=60%; verified baseline1af25c6c; no current candidate state used')
