"""Repeat the bounded native check with the signed absent-local parser correction."""
from pathlib import Path
p=Path(__file__).with_name('check_p419_foreground_nov18.py')
s=p.read_text().replace("out=w/'p419-foreground-native-nov18'","out=w/'p419-foreground-native-nov18b'")
assert s!=p.read_text()
exec(compile(s,str(p),'exec'))
