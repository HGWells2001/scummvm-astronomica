"""Independent PCM16 references for the original P510 button sounds."""
import argparse
import hashlib
import json
import wave
from pathlib import Path

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('root', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    rows = []
    for sound_id in (1, 2, 5):
        path = args.root / f'PLACES/P510/S{sound_id}.WAV'
        with wave.open(str(path)) as wav:
            assert wav.getnchannels() == 1 and wav.getsampwidth() == 1
            raw = wav.readframes(wav.getnframes())
            value = 2166136261
            for sample in raw:
                pcm = ((sample - 128) * 256) & 65535
                for byte in (pcm & 255, pcm >> 8):
                    value = ((value ^ byte) * 16777619) & 0xffffffff
            rows.append(dict(path=path.relative_to(args.root).as_posix(),
                             sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                             rate=wav.getframerate(), samples=len(raw),
                             pcm16le_fnv1a=f'{value:08x}'))
    args.out.write_text(json.dumps(rows, indent=2) + '\n')
    print(rows)
