"""Check exact original-control graph equivalence before and after geometry caching."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
w=Path(__file__).resolve().parent;old=w/'p536-default-graph-nov10e';new=w/'hit-geometry-cache-graph-nov10b'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(old/'proof.json');b=read(new/'proof.json');assert a['status']==b['status']=='P536_REAL_ENGINE_DEFAULT_SETTLED_GRAPH_OBSERVATION_PASS'
def graph(path):return [line.split('] ',1)[1]for line in path.read_text().splitlines()if '] P536 GRAPH 'in line]
before,after=graph(old/'native.log'),graph(new/'native.log');assert before==after
for name in('settled_nodes','original_control_edges','selected_project_terminals','observations'):assert a[name]==b[name]
assert a['settled_nodes']==8 and a['original_control_edges']==120 and not a['native_target_observed']and not b['native_target_observed']
# Timing is descriptive: the host load was not controlled between these runs.
def span(path):
 lines=[line for line in path.read_text().splitlines()if '] 'in line];start=datetime.strptime(lines[0][1:20],'%Y-%m-%d %H:%M:%S');end=datetime.strptime(lines[-1][1:20],'%Y-%m-%d %H:%M:%S');return (end-start).total_seconds()
j=dict(status='HIT_GEOMETRY_P536_ORIGINAL_CONTROL_GRAPH_EQUIVALENCE_PASS',verified_at=datetime.now(timezone.utc).isoformat(),shipping_candidate_exe_sha256=read(w/'hit-geometry-cache-nov10b-stage/proof.json')['candidate_exe_sha256'],baseline_diagnostic_exe_sha256=a['candidate_exe_sha256'],cached_diagnostic_exe_sha256=b['candidate_exe_sha256'],nodes=8,original_exposed_control_edges=120,selected_project_or_scene_exit_terminals=24,predicate_evaluations=a['observations'],graph_rows=len(before),graph_sha256=hashlib.sha256(('\n'.join(before)+'\n').encode()).hexdigest(),baseline_proof_sha256=sha(old/'proof.json'),cached_proof_sha256=sha(new/'proof.json'),baseline_log_seconds=span(old/'native.log'),cached_log_seconds=span(new/'native.log'),target_still_unobserved=True,limits=['Two real-engine diagnostic builds share the shipping production sources; only graph/condition instrumentation differs','Settled default-design paths; idle program/frame epochs normalized, not an exhaustive arbitrary-timing proof','Wall-clock spans are descriptive and not a controlled benchmark or FPS guarantee','No original Windows execution or natural unreachability claim'])
(w/'hit-geometry-cache-graph-review-nov10b.json').write_text(json.dumps(j,indent=2)+'\n');print('Exact P536 control graph unchanged:8nodes/120edges')
