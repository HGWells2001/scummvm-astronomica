"""Independent frame states produced by complete original P510 button clicks."""
from pathlib import Path
import argparse
from verify_move_reference import generate

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('root', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    states = {0: {i: int(i == 10) for i in range(10, 15)},
              1: {i: int(i == 11) for i in range(10, 15)}}
    print(generate(args.root, args.out, 510, 8, ((427, 360),)*2, frame_choices=states))
