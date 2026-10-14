"""Independent P511 frame references from the original four range commands."""
import argparse
from pathlib import Path
from astro_reader import parse
from verify_move_reference import generate

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('root', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    scene = parse((args.root/'PLACES/P511/MEGAFILE.HYP').read_bytes())
    commands = [c for c in scene['scripts'][1] if c['opcode'] == 48]
    assert [c['args'] for c in commands] == [[5,0,1],[5,1,2],[5,2,3],[5,2,3]]
    assert all(c['delay'] == -1 for c in commands)
    assert scene['sprites'][4]['frame_data'] == [500,1,0]
    initial = {i+1:0 for i,s in enumerate(scene['sprites']) if s['clone'] == -1}
    choices = {i:dict(initial) for i in range(4)}
    for i in choices: choices[i][5] = i
    args.out.mkdir(parents=True,exist_ok=True)
    print(generate(args.root,args.out,511,5,((0,204),)*4,frame_choices=choices))
