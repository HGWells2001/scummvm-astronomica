"""Checks against original data, including every truncation of the P0 file."""
import unittest,os
from pathlib import Path
from astro_reader import parse,FormatError
ROOT=Path(os.environ.get('ASTRO_DATA',r'D:\astro'))
class OriginalDataTests(unittest.TestCase):
 def test_p0_reference_script_sequence(self):
  d=parse((ROOT/'PLACES/P0/MEGAFILE.HYP').read_bytes())
  self.assertEqual(d['movies'],['HQLOGO.MOV'])
  self.assertEqual([c['opcode'] for c in d['scripts'][0]],[23,3,31,32,23,42,31,5,45,31,6,42])
  self.assertEqual(d['scripts'][0][1]['args'],[0,160,120,0])
  self.assertEqual(d['scripts'][0][7]['args'],[1]);self.assertEqual(d['scripts'][0][7]['delay'],20000)
 def test_all_p0_truncations_are_rejected(self):
  b=(ROOT/'PLACES/P0/MEGAFILE.HYP').read_bytes()
  for n in range(len(b)):
   with self.subTest(size=n),self.assertRaises(FormatError):parse(b[:n])
 def test_embedded_bitmap_equals_original_file(self):
  b=(ROOT/'PLACES/P0/MEGAFILE.HYP').read_bytes();d=parse(b);bm=d['background']
  self.assertEqual(b[bm['offset']:bm['offset']+bm['size']],(ROOT/'PLACES/P0/BLACK_B').read_bytes())
 def test_corpus_known_exceptions_are_explicit(self):
  failures={};ok=0
  for p in (ROOT/'PLACES').glob('P*/MEGAFILE.HYP'):
   try:parse(p.read_bytes());ok+=1
   except FormatError as e:failures[p.parent.name]=str(e)
  self.assertEqual(ok,416);self.assertEqual(set(failures),{'P406','P502','P503','P504','P533'})
if __name__=='__main__':unittest.main(verbosity=2)
