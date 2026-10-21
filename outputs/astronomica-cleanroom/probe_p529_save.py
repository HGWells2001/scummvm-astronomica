"""Static P529 save inventory from original resources; never runs the game."""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import struct
from astro_reader import parse

ap = argparse.ArgumentParser()
ap.add_argument('root', type=Path)
ap.add_argument('--out', type=Path, required=True)
a = ap.parse_args()
source = a.root / 'PLACES/P529/MEGAFILE.HYP'
raw = source.read_bytes()
s = parse(raw)
assert s['consumed'] == s['size'] == 282102
assert s['mode'] == 0 and s['layers'] == 1
assert len(s['sprites']) == 11 and len(s['scripts']) == 3
assert not s['mouse_rects'] and s['movies'] == ['FUNIV.MOV']
assert s['conditions'] == [[1,0,16,0,0,15],[1,1,1,0,0,1],
                           [1,2,1,0,0,0],[1,3,4,0,0,15]]
assert [len(x.get('frames', [])) for x in s['sprites']] == [2]*7+[16,10,0,0]
assert [x['clone'] for x in s['sprites']] == [-1]*9+[9,9]
assert all(not x['auto_frame'] and not x['auto_move'] and not x['drag_enabled']
           and not x['mouse_in'] and not x['mouse_out'] for x in s['sprites'])

commands = []
def walk(value, path):
    if isinstance(value, dict):
        if 'opcode' in value:
            commands.append(dict(path=path, **value))
        for key, child in value.items():
            walk(child, path+'/'+key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            walk(child, path+'/'+str(i))
walk(s, 'scene')
counts = collections.Counter(c['opcode'] for c in commands)
assert counts[20] == 0 and counts[39] == 0
sprites = []
for i, x in enumerate(s['sprites']):
    owner = i
    visited = set()
    while s['sprites'][owner]['clone'] != -1:
        assert owner not in visited
        visited.add(owner)
        parent = s['sprites'][owner]['clone']-1
        assert 0 <= parent < owner
        owner = parent
    # Only the frame collection comes from the owner. Every mutable field
    # below is taken from this sprite's own serialized record.
    sprites.append(dict(id=i+1, offset=x['offset'], clone=x['clone'],
                        frame_owner=owner+1,
                        frames=len(s['sprites'][owner]['frames']),
                        **{k:x[k] for k in ('layer','visible','xy','click_enabled',
                                           'drag_enabled','rect','auto_frame',
                                           'auto_move','has_cursor')}))
assert [r['frames'] for r in sprites] == [2]*7+[16,10,10,10]
assert [r['xy'] for r in sprites[8:]] == [[445,396],[456,396],[467,396]]
assert sprites[10]['offset']-sprites[9]['offset'] == 64

selection_frames = [c['args'] for c in s['scripts'][0] if c['opcode'] == 15]
assert selection_frames == [[8,i] for i in range(15,-1,-1)]
assert [c['args'] for c in s['sprites'][5]['click'] if c['opcode'] == 46] == [[1,0,-1]]
assert [c['args'] for c in s['sprites'][6]['click'] if c['opcode'] == 46] == [[1,0,1]]
assert [c['args'] for c in s['sprites'][5]['click'] if c['opcode'] == 32] == [[1,0,0]]
assert [c['args'] for c in s['sprites'][6]['click'] if c['opcode'] == 32] == [[1,0,15]]
segments = [c for c in commands if c['opcode'] == 37]
assert [c['args'] for c in segments] == [[0,0,359],[0,1029,232],[0,720,226],[0,360,359]]
assert [c['args'] for c in commands if c['opcode'] == 3] == [[0,160,40,0]]
timers = [c for c in commands if c['opcode'] == 19]
assert [c['args'] for c in timers] == [[11,20,1,0],[10,20,1,0],[9,20,1,0],
                                      [11,-1,1,0],[10,-1,1,0],[9,-1,1,0]]
assert [c['delay'] for c in timers] == [0,-1,-1,4000,-1,-1]
bits = [c for c in commands if c['opcode'] == 33]
assert [c['args'] for c in bits] == [[1,3,2,1],[1,3,3,1],[1,3,1,1],[1,3,0,1]]
movie = (source.parent/'FUNIV.MOV').read_bytes()
def movie_headers(start, end):
    while start+8 <= end:
        size, kind = struct.unpack_from('>I4s', movie, start)
        assert size >= 8 and start+size <= end
        if kind == b'mvhd':
            yield struct.unpack_from('>II', movie, start+20)
        if kind == b'moov':
            yield from movie_headers(start+8, start+size)
        start += size
headers = list(movie_headers(0,len(movie)))
assert headers == [(30,1261)]
assert all(c['args'][1]+c['args'][2] <= 1261 for c in segments)

# A strict atom/table inventory, not a codec or playback probe. All offsets
# below refer directly to the original MOV bytes.
containers = {'moov','trak','mdia','minf','stbl','edts','dinf'}
def atom_tree(start, end):
    result = []
    while start < end:
        assert start+8 <= end
        size, kind = struct.unpack_from('>I4s', movie, start)
        kind = kind.decode('ascii')
        assert 8 <= size <= end-start  # This asset needs no extended-size atoms.
        row = dict(type=kind,offset=start,size=size)
        if kind in containers:
            row['children'] = atom_tree(start+8,start+size)
        result.append(row)
        start += size
    assert start == end
    return result
tree = atom_tree(0,len(movie))
def child(node, kind):
    rows = [r for r in node['children'] if r['type']==kind]
    assert len(rows)==1
    return rows[0]
def full_payload(node):
    p = node['offset']+8
    assert movie[p]==0  # Supported inventory layout is version0 only.
    return p
def table(node, columns):
    p = full_payload(node)
    n = struct.unpack_from('>I',movie,p+4)[0]
    assert node['size']==16+n*4*columns
    return [list(struct.unpack_from('>'+'I'*columns,movie,p+8+4*columns*i)) for i in range(n)]
mdat = next(r for r in tree if r['type']=='mdat')
moov = next(r for r in tree if r['type']=='moov')
tracks = []
for tr in [r for r in moov['children'] if r['type']=='trak']:
    tkhd, mdia = child(tr,'tkhd'),child(tr,'mdia')
    tp = full_payload(tkhd)
    mdhd = child(mdia,'mdhd'); mp = full_payload(mdhd)
    scale,duration = struct.unpack_from('>II',movie,mp+12)
    handler = child(mdia,'hdlr'); hp = full_payload(handler)
    kind = movie[hp+8:hp+12].decode('ascii')
    elst = child(child(tr,'edts'),'elst'); ep = full_payload(elst)
    ne = struct.unpack_from('>I',movie,ep+4)[0]
    assert elst['size']==16+12*ne
    edits = [dict(zip(('movie_duration','media_time','media_rate_16_16'),
                      struct.unpack_from('>Iii',movie,ep+8+12*i))) for i in range(ne)]
    stbl = child(child(mdia,'minf'),'stbl')
    stsd = child(stbl,'stsd'); dp = full_payload(stsd)
    assert struct.unpack_from('>I',movie,dp+4)[0]==1
    entry = dp+8
    entry_size, codec = struct.unpack_from('>I4s',movie,entry)
    assert entry+entry_size == stsd['offset']+stsd['size']
    description = dict(codec=codec.decode('ascii'),offset=entry,size=entry_size,
                       data_reference=struct.unpack_from('>H',movie,entry+14)[0])
    if kind=='vide':
        description.update(width=struct.unpack_from('>H',movie,entry+32)[0],
                           height=struct.unpack_from('>H',movie,entry+34)[0],
                           depth=struct.unpack_from('>H',movie,entry+82)[0])
    elif kind=='soun':
        description.update(channels=struct.unpack_from('>H',movie,entry+24)[0],
                           bits_per_sample=struct.unpack_from('>H',movie,entry+26)[0],
                           sample_rate_16_16=struct.unpack_from('>I',movie,entry+32)[0])
    else:
        raise AssertionError('Unexpected track type')
    stts = table(child(stbl,'stts'),2)
    stsc = table(child(stbl,'stsc'),3)
    stco = [r[0] for r in table(child(stbl,'stco'),1)]
    stsz = child(stbl,'stsz'); zp = full_payload(stsz)
    default_size, count = struct.unpack_from('>II',movie,zp+4)
    sizes = [] if default_size else list(struct.unpack_from('>'+str(count)+'I',movie,zp+12))
    assert stsz['size']==20+(0 if default_size else 4*count)
    assert sum(r[0] for r in stts)==count
    assert sum(n*d for n,d in stts)==duration
    sync_nodes = [r for r in stbl['children'] if r['type']=='stss']
    sync = [r[0] for r in table(sync_nodes[0],1)] if sync_nodes else None
    assert not sync or all(1<=x<=count for x in sync)
    chunks = []; sample = 0; run = 0; sample_offsets = []
    assert stsc[0][0]==1
    for i, offset in enumerate(stco,1):
        while run+1<len(stsc) and stsc[run+1][0]<=i:
            run += 1
        first,n,desc = stsc[run]
        assert desc==1 and sample+n<=count
        byte_count = n*default_size if default_size else sum(sizes[sample:sample+n])
        assert mdat['offset']+8<=offset and offset+byte_count<=mdat['offset']+mdat['size']
        chunks.append(dict(chunk=i,offset=offset,size=byte_count,first_sample=sample+1,samples=n))
        if kind=='vide':
            at = offset
            for j in range(n):
                sample_offsets.append(at);at += sizes[sample+j] if not default_size else default_size
        sample += n
    assert sample==count
    row = dict(id=struct.unpack_from('>I',movie,tp+12)[0],kind=kind,
               movie_duration=struct.unpack_from('>I',movie,tp+20)[0],
               timescale=scale,media_duration=duration,edits=edits,
               matrix= list(struct.unpack_from('>9i',movie,tp+40)),
               display_width_16_16=struct.unpack_from('>I',movie,tp+76)[0],
               display_height_16_16=struct.unpack_from('>I',movie,tp+80)[0],
               description=description,stts=stts,stsc=stsc,chunk_count=len(stco),
               chunks=chunks,stsz=dict(default_size=default_size,sample_count=count,sizes=sizes),
               stss_1based=sync,constant_sample_duration=len({d for n,d in stts})==1)
    if kind=='vide':
        frames = []; tick = 0; frame = 0
        for n,delta in stts:
            for _ in range(n):
                frames.append(dict(index=frame,start_tick=tick,duration_ticks=delta,
                                   offset=sample_offsets[frame],size=sizes[frame],
                                   sync=sync is None or frame+1 in sync))
                tick += delta;frame += 1
        row['frames']=frames
    tracks.append(row)
assert [t['kind'] for t in tracks]==['vide','soun']
video,audio = tracks
assert video['stts']==[[79,3],[1,123],[79,3],[1,123],[53,3],[1,69],[1,81],[37,3],[1,121]]
assert video['stsz']['sample_count']==253 and video['description']['codec']=='cvid'
assert video['description']['width']==320 and video['description']['height']==240
assert video['edits']==[dict(movie_duration=1261,media_time=0,media_rate_16_16=65536)]
assert audio['edits']==[dict(movie_duration=1260,media_time=0,media_rate_16_16=65536)]
assert audio['timescale']==11025 and audio['media_duration']==463050
assert audio['stsz']['default_size']==1 and audio['stsz']['sample_count']==463050
assert audio['description']['codec']=='raw ' and audio['description']['channels']==1
assert audio['description']['bits_per_sample']==8
assert all(t['matrix']==[65536,0,0,0,65536,0,0,0,1073741824] for t in tracks)
segment_samples=[]
for c in segments:
    _,start,length=c['args'];end=start+length
    frames=[f for f in video['frames'] if f['start_tick']<end and f['start_tick']+f['duration_ticks']>start]
    segment_samples.append(dict(start_tick=start,end_tick=end,
      overlapping_indices=[f['index'] for f in frames],
      start_is_sample_boundary=any(f['start_tick']==start for f in frames),
      end_is_sample_boundary=end==1261 or any(f['start_tick']==end for f in video['frames']),
      last_overlapping_frame=frames[-1]))
movie_inventory=dict(atom_tree=tree,movie_timescale=30,movie_duration=1261,
    tracks=tracks,segment_sample_ranges=segment_samples,
    findings=['One video and one audio track, both single nonempty rate1 edit starting at media0; linear monotonic media/movie mapping',
              'Video durations vary: regular3-tick samples plus69/81/121/123-tick holds; do not multiply index by a constant FPS',
              'Audio ends at1260 movie ticks; video ends at1261',
              'Frame sample intervals come from stts only, not observed presentation; engine may stop before the final eligible frame is drawn',
              'All chunk/sample ranges are inside the original mdat; no codec decoding was performed'])
report = dict(date='2026-10-21', status='PASS',
    scope='Static original-resource inventory only; no native save implementation or runtime proof',
    evidence_id='p529-save-original-20261021',
    source=dict(path=str(source),size=len(raw),sha256=hashlib.sha256(raw).hexdigest()),
    reader='astro_reader.py (post-2026-09-13 cleanroom resource parser)',
    consumed=s['consumed'], conditions=s['conditions'], sprites=sprites,
    program_count=len(s['scripts']), mouse_rectangles=0,
    intro_sound_id=s['intro_sound_id'], sounds=s['sounds'],
    command_count=len(commands), opcode_counts={str(k):v for k,v in sorted(counts.items())},
    commands=commands, picture_commits=0, random_commands=0,
    movie=dict(file='FUNIV.MOV',sha256=hashlib.sha256(movie).hexdigest(),
               size=len(movie),timescale=30,duration_ticks=1261,segments=segments,
               static_inventory=movie_inventory),
    selector=dict(local=0,range=[0,15],display_sprite=8,frame_choices=selection_frames,
                  decrement_sprite=6,increment_sprite=7,boundary='clamp, not wrap'),
    outcome_bits=bits, script_started_digit_timers=timers,
    queued_program_calls=[c for c in commands if c['opcode']==41],
    positive_delays=[c for c in commands if c['delay']>0],
    mutation_commands=[c for c in commands if c['opcode'] in (7,15,16,17,18,19,24,30,47,48)],
    requirements=[
      'Preserve all four local values/known flags/metadata, globals, runner metadata, clock/count and RNG consistently with the save format',
      'Preserve eleven independent mutable sprite states; clones10/11 share only sprite9 frame collection',
      'Retain selector display separately from previous outcome digits; changing selector does not itself rewrite digits',
      'Audit queued program calls, foreground audio, movie playback and scripted20ms digit timers before admitting any settled save boundary',
      'Preflight original resource identity and all state before mutation; reject unsupported active work atomically',
      'Compare uninterrupted/restored routes for all16 selectors, repeated outcomes, mask15, success-before-mask15, clamps and unsolved exit; include fresh-process slots and malformed states'],
    unknowns=[
      'No native settled boundary, serializer, restore or playback continuation was executed by this probe',
      'No original runtime was executed; timer phase, stopped timestamps and residual movie pixels require independent native evidence',
      'Custom25 global/counter semantics are not established by this resource-only probe',
      'Absence of opcode20 proves no external background picture commands here; it does not prove movie pixels need no restoration',
      'No overall completion percentage or broader save support follows from this inventory'])
a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('P529 original save inventory PASS:',len(commands),'commands; 11 own sprite states; 4 locals; 6 digit timer commands; no picture commits')
