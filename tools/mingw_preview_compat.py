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
# ScummVM Common::Array has multiple push_back overloads; GCC cannot infer
# the intended value type from an untyped braced-list on this pinned revision.
# Preserve the exact action data and sequence by making the value type explicit.
danger_path = path.with_name('danger.h')
danger = danger_path.read_text(encoding='utf-8')
old_push = 'result.actions.push_back({'
push_count = danger.count(old_push)
if push_count != 161:
    raise SystemExit(f'Unexpected original danger action count: {push_count}; refusing patch')
danger_path.write_text(danger.replace(old_push, 'result.actions.push_back(DangerAction{'), encoding='utf-8')
print(f'MinGW compatibility PASS: {count} QuickTime track references, {push_count} explicit DangerAction values. Only temporary checkout modified.')

