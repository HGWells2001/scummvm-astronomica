from pathlib import Path
lines=Path('work/fresh-20260913/_load_place.asm').read_text().splitlines()
for i,l in enumerate(lines):
 a=int(l[:4],16)
 if (0x1ddb<=a<0x21f2 or 0x29ce<=a<0x2fb2) and ('call     0x2fcd' in l or 'call     0x2ff2' in l or 'cmp ' in l):print('\n'.join(lines[max(0,i-8):i+2]))
