"""Purpose-scoped seed inventory; no project-wide prose search or value reads."""
import os,re,json,shutil
from pathlib import Path
from re_interval_development_budget import ROOT,OUT
from raven_mcs.utils.hashing import sha256_file
SEED=re.compile(r'(?<![\d.])44001(?![\d.])')
if __name__=='__main__':
    matched=[];unread=[];names=[];scanned=0
    ignored={'.git','.venv_new','.venv','node_modules','__pycache__','data','raw','figures','site-packages'}
    evidence_roots=[ROOT,Path('C:/Users/szr/Desktop/record/1')]
    for root in evidence_roots:
        for directory,dirs,files in os.walk(root):
            dirs[:]=[d for d in dirs if d not in ignored and not d.startswith('.venv') and Path(directory)/d!=OUT]
            for name in files:
                path=Path(directory)/name
                if '44001' in name and path.suffix not in {'.py','.md'}:names.append(str(path))
                # Inspect run identities / seed plans, not all project prose.
                upper=name.upper()
                if path.suffix.lower() not in {'.json','.yaml','.yml','.toml','.csv'}:continue
                if not any(x in upper for x in ('MANIFEST','CONFIG','PROTOCOL','SEED','PLAN','RUN_LIST','ACQUISITION','BUDGET')):continue
                try:
                    if path.stat().st_size>2_000_000:continue
                    scanned+=1;text=path.read_text(encoding='utf-8-sig',errors='replace')
                    if SEED.search(text):matched.append(dict(path=str(path),sha256=sha256_file(path),mentions=text.count('44001')))
                except OSError as exc:unread.append(dict(path=str(path),error=str(exc)))
    proposals=[ROOT/'ccf-review-report/revision_feasibility_20261013_125348/NEXT_STAGE_REQUEST.md',
        Path('C:/Users/szr/Desktop/record/1/research-protocols/re-interval-v3-single-development-acquisition-instruction-20261013.md')]
    result=dict(seed=44001,role='development_activation_cost_only',scanned_metadata=scanned,matches=matched,
        named_assets=names,unreadable=unread,scope=[str(p) for p in evidence_roots],
        known_approval_or_proposal=[dict(path=str(p),sha256=sha256_file(p)) for p in proposals],
        status='NO_PRIOR_SELECTION_OR_EXECUTION_FOUND' if not matched and not names and not unread else 'REVIEW_REQUIRED',
        limits='accessible run metadata / seed plans / filenames; not binary-content or inaccessible history proof')
    with (OUT/'SEED_REVIEW.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
    old=ROOT/'results_calibration_first_20261013/PUBLIC_CATALOGUE.parquet'
    shutil.copyfile(old,OUT/'PUBLIC_CATALOGUE.parquet')
    with (OUT/'PUBLIC_CATALOGUE_IDENTITY.json').open('x') as f:json.dump(dict(source=str(old),
        sha256=sha256_file(old),copy_sha256=sha256_file(OUT/'PUBLIC_CATALOGUE.parquet'),
        role='previously published label-free target metadata; no TEST measurements'),f,indent=2)
    print(json.dumps(dict(status=result['status'],scanned=scanned,matches=matched,names=names,unread=unread),ensure_ascii=False))
    if result['status']!='NO_PRIOR_SELECTION_OR_EXECUTION_FOUND':raise SystemExit(2)
