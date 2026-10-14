"""Independent selection-list oracle for the original P505 opcode 39."""
import argparse,json
from pathlib import Path
from astro_reader import parse
if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    scene=parse((args.root/'PLACES/P505/MEGAFILE.HYP').read_bytes())
    commands=[c for s in scene['scripts'] for c in s if c['opcode']==39]
    assert len(commands)==1 and commands[0]['args']==[1,1,1,0]
    condition=next(c for c in scene['conditions'] if c[:2]==[1,1])
    assert condition[2:4]==[8,0]
    candidates=list(range(1,condition[2]+1));state=1;sequence=[];masks=[];mask=0
    while candidates:
        state=(state*0x015a4e35+1)&0xffffffff
        index=((state>>16)&32767)*len(candidates)//32768
        variant=candidates.pop(index);sequence.append(variant)
        mask |= 2**(variant-1);masks.append(mask)
    args.out.write_text(json.dumps(dict(scene=505,opcode=39,args=commands[0]['args'],seed=1,sequence=sequence,masks=masks),indent=2)+'\n')
    print(sequence,masks)
