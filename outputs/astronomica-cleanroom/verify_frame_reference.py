"""Independent original P510 sprite 10 frame selections."""
from pathlib import Path
import argparse
from verify_move_reference import generate
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    print(generate(args.root,args.out,510,8,((427,360),)*3,frame_choices={0:{10:0},1:{10:1},2:{10:0}}))
