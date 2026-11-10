from pathlib import Path
w=Path(__file__).resolve().parent
t=(w/'build_weather_order_fix_nov10.py').read_text().replace('import hashlib,json,os,re,shutil,subprocess','import hashlib,json,os,re,shutil,subprocess,sys')
t=t.replace("b=w/'p523-recipients-nov5-stage/complete-build';s=w/'weather-order-fix-nov10-stage';s.mkdir(exist_ok=False)","fixed='--fixed'in sys.argv\nb=w/'p523-recipients-nov5-stage/complete-build';s=w/('weather-order-audio-fixed-nov10-stage'if fixed else'weather-order-audio-baseline-nov10-stage');s.mkdir(exist_ok=False)")
begin=t.index('from weather_order_source_nov10 import harden');end=t.index('\nbefore=dict(',begin)
t=t[:begin]+'''from weather_order_source_nov10 import harden,add_regression
from weather_order_audio_source_nov10 import inject
if fixed:
    p=src/'script.cpp';p.write_text(harden(p.read_text()))
    p=src/'conditions_test.cpp';p.write_text(add_regression(p.read_text()))
p=src/'astronomica.cpp';p.write_text(inject(p.read_text()))
for n,h in seal['engine_sha256'].items():
    if n not in(('script.cpp','conditions_test.cpp','astronomica.cpp')if fixed else('astronomica.cpp',)):assert sha(src/n)==h
'''+t[end:]
t=t.replace("for name in ('astronomica','script','conditions_test'):","for name in (('astronomica','script','conditions_test')if fixed else('astronomica',)):")
t=t.replace("c=replace(c,b/'obj/astronomica/0005-script.obj',s/'script.obj')\nc=replace(c,b/'obj/astronomica/0001-conditions_test.obj',s/'conditions_test.obj')","if fixed:\n    c=replace(c,b/'obj/astronomica/0005-script.obj',s/'script.obj')\n    c=replace(c,b/'obj/astronomica/0001-conditions_test.obj',s/'conditions_test.obj')")
t=t.replace('WEATHER_ORDER_REAL_ENGINE_CANDIDATE_BUILD_PASS','WEATHER_ORDER_AUDIO_REAL_ENGINE_CANDIDATE_BUILD_PASS').replace('compiled_translation_units=3,reused_verified_foundation_objects=407','compiled_translation_units=3 if fixed else 1,reused_verified_foundation_objects=407 if fixed else 409')
(w/'build_weather_order_audio_nov10.py').write_text(t)
