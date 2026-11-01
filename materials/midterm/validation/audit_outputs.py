#!/usr/bin/env python3
"""Check generated PDF structure, fonts, stable IDs and source question fields.
Requires PyMuPDF and NumPy. Does not replace human visual inspection.
"""
from pathlib import Path
import argparse, json, re
import fitz
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--render-dir', type=Path, help='Optional directory for all PDF pages at 144 dpi')
a = p.parse_args()
locations = json.loads((ROOT/'validation/coverage.json').read_text())['locations']
report = {'checks': [], 'pdfs': {}}
def check(name, passed, detail=None):
    report['checks'].append({'name':name, 'passed':bool(passed), 'detail':detail})

for short, name in [('cheatsheet','CS5486-期中Cheatsheet-双面五栏.pdf'), ('practice','CS5486-期中Cheatsheet-配套例题与解析.pdf')]:
    doc = fitz.open(ROOT/name)
    expected = (841.89,595.28) if short=='cheatsheet' else (595.28,841.89)
    check(short+' A4 and orientation', all(abs(pg.rect.width-expected[0])<.1 and abs(pg.rect.height-expected[1])<.1 for pg in doc))
    check(short+' no blank pages', all(len(pg.get_text().strip())>60 for pg in doc))
    fonts = {f[0]:f[3] for pg in doc for f in pg.get_fonts(full=True)}
    embedded = {font:bool(doc.extract_font(xref)[3]) for xref,font in fonts.items()}
    check(short+' all fonts embedded', all(embedded.values()),len(fonts))
    text = '\n'.join(pg.get_text() for pg in doc)
    check(short+' no excluded algorithms', not re.search(r'MAXNET|kWTA|\bART\b|\bSOM\b',text,re.I))
    info = {'pages':len(doc),'size_points':expected,'font_embedding':embedded,'bookmarks':len(doc.get_toc())}
    if short=='cheatsheet':
        check('exactly two cheatsheet pages',len(doc)==2)
        check('five explicit column headings per page',all(pg.get_text().count('栏｜')==5 for pg in doc))
        margins=[]
        for pg in doc:
            pm=pg.get_pixmap(matrix=fitz.Matrix(3,3),alpha=False)
            rgb=np.frombuffer(pm.samples,dtype=np.uint8).reshape(pm.height,pm.width,3)
            yy,xx=np.where(rgb.min(axis=2)<220)
            margins.append([round(v/3*25.4/72,3) for v in [xx.min(),yy.min(),pm.width-xx.max(),pm.height-yy.max()]])
        info['rendered_ink_margins_mm_LTRB']=margins
        check('cheatsheet printable ink has at least 5mm margins',min(v for row in margins for v in row)>=5,margins)
        all_ids=[i for row in locations.values() for i in row]
        check('all stable knowledge block IDs present',all(i in text for i in all_ids),len(all_ids))
        check('cheatsheet has no external exercise references',not re.search(r'\bQ\d{2}\b|详解|配套例题|混合自测',text))
    else:
        toc=doc.get_toc()
        check('56 question bookmarks',sum(bool(re.search(r'Q\d{2}\b',r[1])) and not 'Q52–Q56' in r[1] for r in toc)==56)
        check('all 56 questions appear',all(f'Q{i:02d}' in text for i in range(1,57)))
    if a.render_dir:
        out=a.render_dir/short;out.mkdir(parents=True,exist_ok=True)
        for i,pg in enumerate(doc,1):pg.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(str(out/f'{i:03d}.png'))
    report['pdfs'][short]=info

source='\n'.join(f.read_text() for f in sorted((ROOT/'practice/sections').glob('*.tex')))
cheat_source='\n'.join((ROOT/'cheatsheet'/name).read_text() for name in ['front.tex','back.tex'])
check('cheatsheet source has no practice macro or Q references',not re.search(r'\\practice\b|\bQ\d{2}\b|详解',cheat_source))
check('procedural and answer-navigation labels are Chinese',not re.search(r'\\textbf\{(?:Calculate|Forward|Branch check|Algebraic solve|Given|Unknown|Answer|Short answer|Copy答句):',cheat_source))
source_locations={}
for column in re.split(r'\\columnstart',cheat_source)[1:]:
    label=re.search(r'\\colhead\{([^｜]+)｜',column)
    if label:
        source_locations[label[1]]=re.findall(r'\\block\{[^}]+\}\{([A-Z]\d{2})\}',column)
check('stable block IDs remain in the original ten columns',source_locations==locations,source_locations)
parts=re.split(r'\\problem\{(Q\d{2})\}',source)
qs=parts[1::2]
check('56 unique stable exercise IDs',len(qs)==len(set(qs))==56 and sorted(qs)==[f'Q{i:02d}' for i in range(1,57)])
missing={}
for i in range(1,len(parts),2):
    q,body=parts[i:i+2]
    fields=[macro for macro in ['qtext','route','given','solve','ans','qcheck','pitfall','transfer'] if not re.search(r'\\'+macro+r'\b',body)]
    if fields:missing[q]=fields
check('every exercise contains all required teaching fields',not missing,missing)
check('coverage table includes each of 187 actual slide pages', sorted(row[0] for row in json.loads((ROOT/'validation/coverage.json').read_text())['pages'])==list(range(1,188)))
report['passed']=all(r['passed'] for r in report['checks'])
(ROOT/'validation/pdf-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'failed':[r for r in report['checks'] if not r['passed']]},ensure_ascii=False))
raise SystemExit(0 if report['passed'] else 1)
