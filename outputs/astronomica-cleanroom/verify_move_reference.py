"""Independent static-subset P517 move references, from original data."""
from pathlib import Path
from io import BytesIO
import argparse, json
from PIL import Image
from astro_reader import parse

def generate(root, out, scene_id=517, sprite_id=7, positions=((447,361),(477,361)), overrides=None, frame_choices=None, visibility_choices=None, background_patches=None):
    data=(root/f'PLACES/P{scene_id}/MEGAFILE.HYP').read_bytes(); scene=parse(data)
    assert scene['layers']==1
    def bmp(ref): return Image.open(BytesIO(data[ref['offset']:ref['offset']+ref['size']])).convert('RGB')
    reports=[]
    for step,(x,y) in enumerate(positions):
        canvas=Image.new('RGB',(640,480))
        if scene['background']: canvas.paste(bmp(scene['background']),(0,0))
        if scene['control']:
            control=bmp(scene['control']);canvas.paste(control,(0,480-control.height))
        if background_patches:
            name,px,py=background_patches[step]; canvas.paste(Image.open(root/f"PLACES/P{scene_id}/{name}").convert("RGB"),(px,py))
        drawn=0
        for i,s in enumerate(scene['sprites']):
            if not (visibility_choices or {}).get(step,{}).get(i+1,s['visible']) or s['layer']!=1: continue
            source=i
            while scene['sprites'][source]['clone']!=-1:
                parent=scene['sprites'][source]['clone']-1
                assert 0<=parent<source
                source=parent
            frames=scene['sprites'][source]['frames']
            frame=(frame_choices or {}).get(step,{}).get(i+1,0 if len(frames)==1 else -1)
            if frame<0: continue
            image,mask=map(bmp,frames[frame]); assert image.size==mask.size
            pos=(x,y) if i==sprite_id-1 else tuple(s['xy'])
            pos=(overrides or {}).get(step,{}).get(i+1,pos)
            canvas.paste(image,pos,mask.convert('L').point(lambda v:255-v));drawn+=1
        hashes={}
        for bits in (888,565):
            h=2166136261
            for i,v in enumerate(canvas.crop((0,0,640,456)).tobytes()):
                if bits==565:
                    n=v>>(2 if i%3==1 else 3);v=((n<<2)|(n>>4)) if i%3==1 else ((n<<3)|(n>>2))
                h=((h^v)*16777619)&0xffffffff
            hashes[str(bits)]=f'{h:08x}'
        canvas.save(out/f'P{scene_id}-{step}-x{x}-y{y}.png'); reports.append(dict(sprite=sprite_id,x=x,y=y,drawn=drawn,hashes=hashes))
    assert reports[0]['hashes']!=reports[1]['hashes']
    (out/f'P{scene_id}-movement.json').write_text(json.dumps(reports,indent=2));return reports

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True);print(generate(args.root,args.out))
