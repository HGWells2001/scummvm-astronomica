"""Distinguish scene progression from valid real-time movie playback."""
import re
def timing_valid(text):
    p2=text.find('Astronomica resource explorer: P2;')
    p3=text.find('Astronomica resource explorer: P3;')
    end=text.find('Astronomica movie segment finished:',p2)
    closed=re.findall(r'movie closed while playing: \d+ frames, time (\d+), end (\d+)',text)
    return (0<=p2<end<p3 and len(closed)==1 and
            69500<=int(closed[0][0])<=70500 and int(closed[0][1])==71100)
