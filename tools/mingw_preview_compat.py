# SPDX-License-Identifier: GPL-3.0-or-later
"""Narrow MinGW-only qualification of the QuickTime audio track enum.

This patch is applied to the *temporary pinned ScummVM checkout*, never to
the hashed/canonical engine in outputs/. It makes the MSVC-compatible
unqualified member name unambiguous to GCC without changing behavior.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'work/fresh-20260913/scummvm/engines/astronomica/astronomica.cpp'
source = path.read_text(encoding='utf-8')
old = 'Track::kTrackTypeAudio'
new = 'Video::VideoDecoder::Track::kTrackTypeAudio'
count = source.count(old)
if count != 5:
    raise SystemExit(f'Unexpected ASVM31 audio track references: {count}; refusing to patch')
path.write_text(source.replace(old, new), encoding='utf-8')
print(f'MinGW preview audio-track name qualification PASS: {count} references; only temporary checkout modified')
