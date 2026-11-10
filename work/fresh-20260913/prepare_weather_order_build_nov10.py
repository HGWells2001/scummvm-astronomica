from pathlib import Path
w=Path(__file__).resolve().parent
t=(w/'build_builder_mask_guard_nov9.py').read_text()
t=t.replace("s=w/'builder-mask-guard-nov9-stage'","s=w/'weather-order-fix-nov10-stage'").replace("w/'opening-rgb-seal-nov6-status.json'","w/'builder-mask-guard-seal-nov9-status.json'")
t=t.replace("if name!='astronomica.cpp':assert sha(b/'source/engines/astronomica'/name)==h","if name!='astronomica.cpp':assert sha(b/'source/engines/astronomica'/name)==h")
begin=t.index('from builder_profile_guard_source_nov9 import harden');end=t.index('\nbefore=dict(',begin)
t=t[:begin]+'''from weather_order_source_nov10 import harden,add_regression
p=src/'script.cpp';p.write_text(harden(p.read_text()))
p=src/'conditions_test.cpp';p.write_text(add_regression(p.read_text()))
for n,h in seal['engine_sha256'].items():
    if n not in('script.cpp','conditions_test.cpp'):assert sha(src/n)==h
'''+t[end:]
t=t.replace("for name in ('astronomica',):","for name in ('astronomica','script','conditions_test'):")
# The current main's ASTRO differs from the clean foundation; freshly compile
# that unchanged current unit too instead of silently linking its old object.
t=t.replace("c=replace(c,b/'bin/astronomica.lib',s/'bin/astronomica.lib');run('lib',c,'lib')", "c=replace(c,b/'obj/astronomica/0005-script.obj',s/'script.obj')\nc=replace(c,b/'obj/astronomica/0001-conditions_test.obj',s/'conditions_test.obj')\nc=replace(c,b/'bin/astronomica.lib',s/'bin/astronomica.lib');run('lib',c,'lib')")
t=t.replace('BUILDER_PROFILE_GUARD_ENGINE_CANDIDATE_BUILD_PASS','WEATHER_ORDER_REAL_ENGINE_CANDIDATE_BUILD_PASS').replace('compiled_translation_units=1,reused_verified_foundation_objects=409','compiled_translation_units=3,reused_verified_foundation_objects=407')
(w/'build_weather_order_fix_nov10.py').write_text(t)
