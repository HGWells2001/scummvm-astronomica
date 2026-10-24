"""Fresh original P509 inventory; static evidence, no original runtime execution."""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from astro_reader import parse


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root', type=Path)
    ap.add_argument('--out', type=Path, default=HERE/'evidence/p509-save-original.json')
    args = ap.parse_args()
    path = args.root/'PLACES/P509/MEGAFILE.HYP'
    data = path.read_bytes()
    assert len(data) == 713948
    assert digest(data) == '053c47d65ba963ed0b1f4fc78f088fa1678586ed6a02c6c1178772e22f572e44'
    scene = parse(data)
    assert scene['mode'] == 0 and scene['layers'] == 1
    assert len(scene['sprites']) == 19 and len(scene['conditions']) == 17
    assert len(scene['scripts']) == 6
    commands = []

    def walk(value, location):
        if isinstance(value, dict):
            if 'opcode' in value:
                commands.append(dict(location=location, **value))
            for key, child in value.items():
                walk(child, location+'/'+key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, location+'/'+str(index))

    walk(scene, 'scene')
    assert len(commands) == 312
    assert len(scene['scripts'][5]) == 25
    assert scene['scripts'][5][3]['opcode'] == 31
    assert scene['scripts'][5][3]['delay'] == 800
    assert scene['scripts'][5][24]['opcode'] == 41
    assert scene['scripts'][5][24]['args'] == [5]
    fnv = 2166136261
    for byte in data:
        fnv = ((fnv ^ byte) * 16777619) & 0xffffffff
    assert fnv == 3651436523
    sprites = []
    for index, sprite in enumerate(scene['sprites']):
        assert sprite['clone'] == -1
        sprites.append(dict(id=index+1,
            geometry=[[frame[0]['width'], frame[0]['height']] for frame in sprite['frames']],
            **{key: value for key, value in sprite.items() if key != 'frames'}))
    assets = []
    for file in sorted(path.parent.iterdir()):
        if file.is_file() and file != path:
            raw = file.read_bytes()
            assets.append(dict(name=file.name, size=len(raw), sha256=digest(raw)))
    assert {'SKY1', 'SKY2', 'SKY3'} <= {row['name'].upper() for row in assets}
    result = dict(status='STATIC_ORIGINAL_PROFILE_ONLY', date='2026-10-24',
        source=dict(path=str(path), size=len(data), sha256=digest(data), fnv1a32=fnv),
        reader_sha256=digest((HERE/'astro_reader.py').read_bytes()),
        mode=scene['mode'], layers=scene['layers'], sprite_count=19, condition_count=17,
        startup_program_count=6, command_count=len(commands),
        opcode_counts=dict(sorted(collections.Counter(c['opcode'] for c in commands).items())),
        background=scene['background'], control=scene['control'], conditions=scene['conditions'],
        programs=scene['scripts'], mouse_rects=scene['mouse_rects'], sprites=sprites,
        sounds=scene['sounds'], movies=scene['movies'], assets=assets, commands=commands,
        candidate_boundary=dict(trusted_program=5, index=3, delay_ms=800,
            phase=[1, 2], scheduler_words=608, sprite_words=27,
            requirements=['One pending original narrator, no other queued work or actions',
                'No foreground audio, lock, movie, transient image or transition',
                'Fresh configured live runner binding; no replay of startup']),
        findings=['Six startup programs plus sprite/rectangle handlers: not22 startup programs.',
            'Original program5 self-schedules with opcode41;605 persistent words alone omit its pending epoch.',
            'Conditional scheduling and since/loadedAt require exact future execution tests.',
            'Hidden sprite11 keeps independent150ms frame and200ms bounce movement clocks.',
            'Preserve external SKY image identity and retained sprite history independently of local phase.'],
        limitations=['Static data does not prove native reachability or correct save restoration.',
            'No original ASTRO.EXE runtime execution or full audiovisual playthrough.',
            'Candidate contract is provisional until engine and independent continuation tests pass.'])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(args.out)


if __name__ == '__main__':
    main()
