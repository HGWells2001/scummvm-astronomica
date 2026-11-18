"""Map current native navigation fixtures to versioned candidate requirements."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,collections,hashlib,json,re,traceback
ap=argparse.ArgumentParser();ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();w=a.workspace.resolve();out=a.out.resolve();out.mkdir(exist_ok=False,parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
try:
    native=w/'navigation-music-native-nov18b';stage=w/'navigation-music-observer-nov18b-stage';fixture=w/'navigation-music-cases-nov18.json';syntax=w/'original-branches-nov6/inventory.json';catalogue=w/'original-behavior-requirements-nov17'
    p=read(native/'proof.json');build=read(stage/'proof.json');cases=read(fixture);inv=read(syntax);catalog=read(catalogue/'requirements-local.json');cp=read(catalogue/'proof.json')
    assert p['status']=='ORIGINAL_NAVIGATION_ACTIVE_MUSIC_PASS' and sha(native/'native.log')==p['native_log_sha256']
    assert sha(fixture)==p['cases_sha256'] and sha(stage/'proof.json')==p['observer_build_proof_sha256']
    assert sha(stage/'bin/scummvm.exe')==p['observer_exe_sha256']==build['candidate_exe_sha256']
    assert sha(stage/'source/engines/astronomica/astronomica.cpp')==build['candidate_engine_sha256']['astronomica.cpp']
    assert sha(w/'build/Releasex64/scummvm.exe')==p['canonical_exe_sha256']==build['base_exe_sha256']
    assert cp['local_detail_sha256']==sha(catalogue/'requirements-local.json') and cp['syntax_inventory_sha256']==cases['route_inventory_sha256']==sha(syntax)
    byid={r['id']:r for r in catalog['requirements']};lines={}
    for n,line in enumerate((native/'native.log').read_text(errors='replace').splitlines(),1):
        m=re.search(r'Navigation Music row: case(\d+) route(\d+) .* resultPASS$',line)
        if m:
            case,route=map(int,m.groups());assert case not in lines and cases['cases'][case]['route_index']==route;lines[case]=n
    assert set(lines)==set(range(1538));rows=[];linked=set();per_source=collections.Counter()
    for case,c in enumerate(cases['cases']):
        index=c['route_index'];rid='literal_route_outcome:'+str(index);req=byid[rid];ref=inv['route_references'][index]
        assert req['kind']=='literal_route_outcome' and req['route_kind']=='navigation' and req['source_scene']==ref['source']==c['source']
        assert ref['destination']==c['requested'] and ref['kind']=='navigation'
        linked.add(rid);per_source[c['source']]+=1
        rows.append(dict(requirement_id=rid,case=case,source=c['source'],direction=c['direction'],literal_destination=c['requested'],controlled_permit=c['permit'],keypad=bool(c['keypad']),original_expected_destination=c['destination'],original_expected_permit_after=c['permit_after'],expected_source_loop=c['source_loop'],expected_destination_loop=c['destination_loop'],native_pass_log_line=lines[case],current_handler_destination_verified=True,current_active_music_boundary_verified=True,natural_reachability='UNCLASSIFIED',complete_requirement_verified=False))
    assert len(linked)==760 and len(per_source)==305
    local=out/'navigation-requirements-local.json';local.write_text(json.dumps(dict(schema_version=1,rows=rows),indent=2)+'\n')
    proof=dict(status='CURRENT_NAVIGATION_MUSIC_REQUIREMENT_MAP_PASS',schema_version=1,at=datetime.now(timezone.utc).isoformat(),author_sha256=sha(Path(__file__)),behavior_catalogue_sha256=sha(catalogue/'proof.json'),syntax_inventory_sha256=sha(syntax),native_proof_sha256=sha(native/'proof.json'),native_log_sha256=sha(native/'native.log'),observer_build_proof_sha256=sha(stage/'proof.json'),observer_exe_sha256=p['observer_exe_sha256'],canonical_exe_sha256=p['canonical_exe_sha256'],cases_sha256=sha(fixture),local_detail_sha256=sha(local),candidate_literal_route_requirements=1124,navigation_candidate_requirements_linked=760,script_place_candidate_requirements_not_inferred=364,native_controlled_cases=1538,source_scenes_with_routes=305,mode1_scene_without_nav_routes=31,per_source_controlled_cases={str(k):v for k,v in sorted(per_source.items())},engine_changed=False,acceptance_A03_complete=False,whole_game_completion_percent=None,limits=['Current verified production source plus isolated observation only; observer executable is not deployed','Per-case original transition oracle, real arrow/keypad handler, active and advancing Music through normal frame pump','Controlled direct loads and selected global57 values do not establish natural reachability or exhaustive global/timing combinations','Sprite clicks and364 script-place operands are outside this measurement','This links bounded evidence; candidate requirements remain incomplete as full behavior claims'])
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof['status'],len(linked),len(rows))
except Exception:
    (out/'failure.json').write_text(json.dumps(dict(status='FAILED',error=traceback.format_exc()),indent=2)+'\n');raise
