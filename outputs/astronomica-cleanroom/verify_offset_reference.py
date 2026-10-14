"""P510 independent references for two executions of original opcode 47."""
from pathlib import Path
import argparse
from verify_move_reference import generate
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    print(generate(args.root,args.out,510,8,((427,360),(427,361),(427,362),(427,363),(427,363)),{4:{9:(513,362)}}))
