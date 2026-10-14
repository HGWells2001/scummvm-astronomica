import zipfile
for file in ['scummclassic.zip','scummmodern.zip']:
 z=zipfile.ZipFile('work/fresh-20260913/scummvm/gui/themes/'+file);print(file,[s for s in z.namelist() if s.endswith(('.bdf','.fcc'))])
