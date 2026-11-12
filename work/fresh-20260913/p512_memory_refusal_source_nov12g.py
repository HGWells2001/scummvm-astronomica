"""Apply the production replay fix and the exact under-end clock regression observer."""
from p512_segment_replay_source_nov12 import inject as replay
from p512_memory_refusal_source_nov12f import inject as observer


def inject(cpp, script):
    return observer(*replay(cpp, script))
