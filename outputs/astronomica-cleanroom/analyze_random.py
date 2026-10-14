"""Extract the original RNG constants and independent reference vectors."""
import argparse,hashlib,json,struct
from pathlib import Path
if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    b=(args.root/'SETUP/ASTRO.EXE').read_bytes()
    assert hashlib.sha256(b).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
    ne=struct.unpack_from('<I',b,60)[0];table=ne+struct.unpack_from('<H',b,ne+0x22)[0]
    base=struct.unpack_from('<H',b,table)[0]<<struct.unpack_from('<H',b,ne+0x32)[0]
    assert b[base+0xb75]==0xba and b[base+0xb78]==0xb8
    multiplier=(struct.unpack_from('<H',b,base+0xb76)[0]<<16)|struct.unpack_from('<H',b,base+0xb79)[0]
    rows=[]
    for seed in (0,1,65535):
        state=seed;draws=[]
        for i in range(12):
            state=(state*multiplier+1)&0xffffffff
            draws.append((state>>16)&32767)
        rows.append(dict(seed=seed,draws=draws,range_1_3=[1+(v*3)//32768 for v in draws]))
    result=dict(multiplier=hex(multiplier),increment=1,state_bits=32,output_bits=15,vectors=rows,
                evidence=['1:0b3c multiply','1:0b54 srand','1:0b6b rand','15:1d20 RangedRdm'])
    args.out.write_text(json.dumps(result,indent=2)+'\n');print(result)
