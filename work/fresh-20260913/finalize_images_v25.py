from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp');s=p.read_text().replace(' file.seek(0); Image::BitmapDecoder decoder;', ' // The shared decoder excludes monochrome external bitmaps.\n file.seek(28); if (file.readUint16LE() == 1) return nullptr;\n file.seek(0); Image::BitmapDecoder decoder;');p.write_text(s)
import shutil
shutil.copy2(p,Path('work/fresh-20260913/scummvm/engines/astronomica')/p.name)
p=Path('outputs/astronomica-cleanroom/survey_puzzles.py');s=p.read_text().replace("ap.add_argument('--out',type=Path,required=True);", "ap.add_argument('--runtime-log',type=Path);ap.add_argument('--out',type=Path,required=True);").replace('16,17,23,25','16,17,20,23,25').replace('47,48,51}', '47,48,49,51}');s+='''
if args.runtime_log:
    coverage=[dict(scene=int(p),accepted=int(a),total=int(t)) for p,a,t in re.findall(r'Astronomica puzzle coverage: P(\\d+) entry=(\\d+)/(\\d+)',args.runtime_log.read_text())]
    assert len(coverage)==len(rows)
    accepted=sum(r['accepted'] for r in coverage);total=sum(r['total'] for r in coverage)
    (args.out/'evidence/puzzle-coverage.json').write_text(json.dumps(dict(metric='Static canRun validation, audio enabled; not execution/playability',accepted=accepted,total=total,scenes=coverage),indent=2))
    with (args.out/'PUZZLE-SURVEY.md').open('a') as f:
        f.write('\\n## Controllo nativo degli script\\n\\n'+f'{accepted}/{total} template superano canRun. Non e una percentuale di gioco completabile, ne una prova di esecuzione.\\n\\n| Scena | Template validati |\\n|---|---:|\\n')
        for r in coverage:f.write(f"| P{r['scene']} | {r['accepted']}/{r['total']} |\\n")
        f.write('\\nGli opcode 20/49 sono ammessi soltanto in coppia consecutiva, con visualizzazione immediata, file BMP decodificabile e scena a un livello. I casi separati da diramazioni, come P508, restano esclusi.\\n')
    print('Native validation:',accepted,'/',total)
''';p.write_text(s)
