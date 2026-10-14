"""Pillow references for the original P510 indicator, with initial frames."""
import argparse
from pathlib import Path
from astro_reader import parse
from verify_move_reference import generate

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('root', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    scene = parse((args.root/'PLACES/P510/MEGAFILE.HYP').read_bytes())
    assert scene['sprites'][1]['frame_data'] == [400, 1, 0]
    assert [(c['opcode'],c['args'],c['delay']) for c in scene['sprites'][6]['click']] == [
        (28,[-1],0),(16,[2],0),(29,[-1],400),(17,[2],10000)]
    initial = {i+1: 0 for i,s in enumerate(scene['sprites']) if s['clone'] == -1}
    choices = {0: initial, 1: dict(initial)}
    choices[1][2] = 1
    choices[1][7] = 1  # Built-in type-2 button pulse remains pressed at 400 ms.
    args.out.mkdir(parents=True, exist_ok=True)
    print(generate(args.root,args.out,510,8,((427,360),)*2,
                   frame_choices=choices,visibility_choices={0:{2:1},1:{2:1}}))
