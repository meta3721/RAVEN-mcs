from pathlib import Path
import json, re, importlib.util
from pypdf import PdfReader

root=Path('C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean')
before=Path('C:/Cursor/raven.mcs/tmp/remaining_compress')
out=Path(__file__).parent
result={'scope':'Read-only paper extraction and textual evidence preservation, no training or compilation', 'pdfs':{}, 'comparison':{}}
for name in ['main','supplemental']:
    r=PdfReader(root/(name+'.pdf'))
    pages=[p.extract_text() or '' for p in r.pages]
    (out/(name+'-pages.json')).write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/(name+'-fulltext.txt')).write_text('\n\n'.join(f'=== PAGE {i+1} ===\n{t}' for i,t in enumerate(pages)),encoding='utf-8')
    fonts={}
    for p in r.pages:
        res=p.get('/Resources',{}).get_object()
        for f in res.get('/Font',{}).get_object().values():
            f=f.get_object()
            fd=f.get('/FontDescriptor')
            if fd: fd=fd.get_object()
            fonts[str(f.get('/BaseFont'))]={'subtype':str(f.get('/Subtype')),'embedded':bool(fd and any(k in fd for k in ['/FontFile','/FontFile2','/FontFile3']))}
    result['pdfs'][name]={'pages':len(pages),'bytes':(root/(name+'.pdf')).stat().st_size,'dimensions_pt':[float(x) for x in r.pages[0].mediabox], 'metadata':{str(k):str(v) for k,v in (r.metadata or {}).items()}, 'fonts':fonts, 'unresolved_mark_pages':[i+1 for i,t in enumerate(pages) if '??' in t], 'page_headers':[{'page':i+1,'head':' '.join(t.split()[:19])} for i,t in enumerate(pages)]}

def envs(text,kind):
    return re.findall(r'\\begin\{'+kind+r'\*?\}.*?\\end\{'+kind+r'\*?\}',text,re.S)
def label(block):
    m=re.search(r'\\label\{([^}]+)\}',block)
    return m.group(1) if m else None
def compact(s): return re.sub(r'\s+','',s)
def table_body(b):
    m=re.search(r'\\begin\{tabular\*?\}.*?\\end\{tabular\*?\}',b,re.S)
    return compact(m.group(0)) if m else compact(b)
for name in ['main.tex','appendix.tex','supplemental.tex']:
    old=(before/(name+'.before')).read_text(encoding='utf-8-sig')
    new=(root/name).read_text(encoding='utf-8-sig')
    a={label(x):x for x in envs(old,'table')}
    b={label(x):x for x in envs(new,'table')}
    oa={label(x):x for x in envs(old,'figure')}
    nb={label(x):x for x in envs(new,'figure')}
    old_math={label(x):compact(x) for kind in ['equation','align','multline'] for x in envs(old,kind) if label(x)}
    new_math={label(x):compact(x) for kind in ['equation','align','multline'] for x in envs(new,kind) if label(x)}
    result['comparison'][name]={'tables_before':len(a),'tables_after':len(b),'table_labels_removed':list(a.keys()-b.keys()),'table_labels_added':list(b.keys()-a.keys()),'table_bodies_changed':[k for k in a.keys()&b.keys() if table_body(a[k])!=table_body(b[k])], 'figures_before':len(oa),'figures_after':len(nb),'figure_labels_removed':list(oa.keys()-nb.keys()),'numbered_math_before':len(old_math),'numbered_math_after':len(new_math),'math_removed':list(old_math.keys()-new_math.keys()),'math_added':list(new_math.keys()-old_math.keys()),'math_changed':[k for k in old_math.keys()&new_math.keys() if old_math[k]!=new_math[k]]}
    if name=='main.tex':
        cutoff='\\section{Theoretical Analysis}'
        result['comparison'][name]['pre_VI_unchanged']=old.split(cutoff)[0]==new.split(cutoff)[0]

result['render_pdfium_available']=bool(importlib.util.find_spec('pypdfium2'))
(out/'inspection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='pdfs'},ensure_ascii=False,indent=2))
print(json.dumps({k:{j:v[j] for j in ['pages','unresolved_mark_pages','dimensions_pt']} for k,v in result['pdfs'].items()},ensure_ascii=False))
