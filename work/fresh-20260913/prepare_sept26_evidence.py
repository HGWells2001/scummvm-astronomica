from pathlib import Path

p = Path('outputs/astronomica-cleanroom/probe_p526_answers.py')
s = p.read_text()
s = s.replace('Research only; movement and full route remain unimplemented','Original comparison-chain evidence; engine integration verified separately')
s = s.replace('cases_executed=6*14*7,accepted_choices','cases_executed=6*14*7,extra_scenario_boundary_cases=3*14*7,accepted_choices')
p.write_text(s)
p = Path('work/fresh-20260913/save_development_evidence.py')
s = p.read_text().replace('2026-09-25 evening','2026-09-26').replace('521,525,527','521,525,526,527')
if 'P526 interaction verification' not in s:
    s = s.replace("assert 'variant puzzle verification: PASS' in log", "assert 'variant puzzle verification: PASS' in log\nassert 'P526 interaction verification: PASS' in log\nassert 'P526 original motion comparison: PASS' in log")
p.write_text(s)
