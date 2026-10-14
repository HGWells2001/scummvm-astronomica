"""Independent P29 static composition from original bitmaps using Pillow."""
from pathlib import Path
from io import BytesIO
import argparse, json
from PIL import Image
from astro_reader import parse

def reference(root, output):
    data=(root/'PLACES/P29/MEGAFILE.HYP').read_bytes(); scene=parse(data)
    def bitmap(ref): return Image.open(BytesIO(data[ref['offset']:ref['offset']+ref['size']])).convert('RGB')
    image=Image.new('RGB',(640,480)); image.paste(bitmap(scene['background']),(0,0))
    hidden=image.crop((0,0,640,456)).tobytes()
    count=0
    for sprite in scene['sprites']:
        if not sprite['visible']: continue
        assert sprite['clone']==-1 and sprite['layer']==1 and len(sprite['frames'])==1
        src,mask=map(bitmap,sprite['frames'][0]); assert src.size==mask.size
        raw=mask.tobytes(); assert all(raw[i:i+3] in (b'\0\0\0',b'\xff\xff\xff') for i in range(0,len(raw),3))
        alpha=mask.convert('L').point(lambda v:255-v)
        image.paste(src,tuple(sprite['xy']),alpha); count+=1
    assert count==1
    # Ignore the explorer caption occupying the last 24 rows.
    digest=2166136261
    for value in image.crop((0,0,640,456)).tobytes(): digest=((digest^value)*16777619)&0xffffffff
    quantized=bytearray()
    for i,v in enumerate(image.crop((0,0,640,456)).tobytes()):
        n=v>>(2 if i%3==1 else 3)
        quantized.append(((n<<2)|(n>>4)) if i%3==1 else ((n<<3)|(n>>2)))
    digest565=2166136261
    for v in quantized: digest565=((digest565^v)*16777619)&0xffffffff
    image.save(output)
    hidden_hashes={}
    for mode in (888,565):
        h=2166136261
        for i,v in enumerate(hidden):
            if mode==565:
                n=v>>(2 if i%3==1 else 3)
                v=((n<<2)|(n>>4)) if i%3==1 else ((n<<3)|(n>>2))
            h=((h^v)*16777619)&0xffffffff
        hidden_hashes[str(mode)]=f'{h:08x}'
    return dict(scene='P29',sprites=count,rgb_fnv1a_640x456=f'{digest:08x}',rgb565_fnv1a_640x456=f'{digest565:08x}',hidden_fnv1a=hidden_hashes,source='Original bitmaps, independently decoded and composed with Pillow')

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('root',type=Path); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
    result=reference(args.root,args.out); args.out.with_suffix('.json').write_text(json.dumps(result,indent=2)); print(result)
