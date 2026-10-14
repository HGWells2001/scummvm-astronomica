"""Measure the test-only SDL dummy audio clock without video or game code."""
import ctypes as c
import os, time, json
from pathlib import Path
base = Path(__file__).resolve().parent
os.environ['SDL_AUDIODRIVER'] = 'dummy'
dll = c.CDLL(str(base / 'build/Releasex64/SDL2.dll'))
callback_type = c.CFUNCTYPE(None, c.c_void_p, c.POINTER(c.c_uint8), c.c_int)
class Spec(c.Structure):
    _fields_ = [('freq', c.c_int), ('format', c.c_uint16), ('channels', c.c_uint8),
               ('silence', c.c_uint8), ('samples', c.c_uint16), ('padding', c.c_uint16),
               ('size', c.c_uint32), ('callback', callback_type), ('userdata', c.c_void_p)]
samples = 0
@callback_type
def callback(userdata, stream, length):
    global samples
    c.memset(stream, 0, length)
    samples += length // 4
dll.SDL_InitSubSystem.argtypes = [c.c_uint32]
dll.SDL_OpenAudio.argtypes = [c.POINTER(Spec), c.POINTER(Spec)]
assert dll.SDL_InitSubSystem(0x10) == 0
desired = Spec(freq=44100, format=0x8010, channels=2, samples=1024, callback=callback)
obtained = Spec()
assert dll.SDL_OpenAudio(c.byref(desired), c.byref(obtained)) == 0
start = time.perf_counter()
dll.SDL_PauseAudio(0)
time.sleep(12)
dll.SDL_PauseAudio(1)
wall = time.perf_counter()-start
dll.SDL_CloseAudio()
dll.SDL_QuitSubSystem(0x10)
result = dict(driver='dummy', wall_seconds=wall, audio_seconds=samples/obtained.freq,
              ratio=(samples/obtained.freq)/wall, samples=samples, rate=obtained.freq,
              buffer=obtained.samples, scope='Diagnostic only; no engine changes')
(base/'sdl-dummy-clock.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
