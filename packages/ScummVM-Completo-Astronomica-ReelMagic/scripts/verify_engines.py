"""Reject a partial generated solution before compiling or downloading libraries."""
from pathlib import Path
import json
import re
import sys

source, build = (Path(p).resolve() for p in sys.argv[1:])
expected = set()
for config in (source / 'engines').glob('*/configure.engine'):
    name = config.parent.name
    if re.search(r'^add_engine\s+' + re.escape(name) + r'\s', config.read_text(), re.M):
        expected.add(name)
actual = {p.stem for p in build.glob('*.vcxproj')} - {'scummvm', 'scummvm-detection'}
solution = (build / 'scummvm.sln').read_text()
definitions = (build / 'ScummVM_Globalx64.props').read_text()
for name in sorted(expected):
    if name not in actual or '"' + name + '.vcxproj"' not in solution:
        raise SystemExit('Progetto engine mancante: ' + name)
    if 'ENABLE_' + name.upper() + ';' not in definitions:
        raise SystemExit('Engine disabilitato: ' + name)
if not {'astronomica', 'made'}.issubset(expected):
    raise SystemExit('Sorgenti dei motori aggiuntivi mancanti')
report = dict(status='ALL_ENGINE_PROJECTS_PASS', count=len(expected), engines=sorted(expected))
(build / 'ALL-ENGINES.json').write_text(json.dumps(report, indent=2) + '\n')
print('Verificati tutti i', len(expected), 'progetti engine, Astronomica e MADE inclusi.')
