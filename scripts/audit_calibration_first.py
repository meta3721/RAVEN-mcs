"""Read-only seed membership and public metadata inventory before first run."""
import os, re, json, hashlib
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results_calibration_first_20261013'

def main():
    matches=[];names=[];scanned=0;skipped=[]
    roots=[ROOT,Path('C:/Users/szr/Desktop/record/1')]
    ignore={'.git','.venv','.venv_new','.venv_old','node_modules','__pycache__','.codex','.agents'}
    pattern=re.compile(r'(?<![\d.])43001(?![\d.])')
    for root in roots:
        for directory,dirs,files in os.walk(root):
            dirs[:]=[d for d in dirs if d not in ignore and not d.startswith('.venv') and Path(directory)/d!=OUT]
            for name in files:
                f=Path(directory)/name
                if '43001' in name:names.append(str(f))
                if f.suffix.lower() not in {'.json','.jsonl','.yaml','.yml','.toml','.md','.py','.csv','.txt','.tex'}:continue
                # Do not expose raw private value tables. Seed traces are audited by names and metadata.
                if any(p in {'raw','client_measurements','site-packages'} for p in f.parts):continue
                scanned+=1
                try:
                    with f.open(encoding='utf-8-sig',errors='replace') as stream:
                        for i,line in enumerate(stream,1):
                            if pattern.search(line):matches.append(dict(path=str(f),line=i,text=line.strip()[:500]))
                except OSError as exc:skipped.append(dict(path=str(f),reason=str(exc)))
    known_proposals={'Q_CALIBRATION_PLAN.md','NEXT_STAGE_READINESS.md'}
    conflicts=[]
    for m in matches:
        f=Path(m['path'])
        if f.name in known_proposals and 'conditional_bundle_b0_20261012_223821' in f.parts:continue
        if f==Path(__file__).resolve() or f==ROOT/'scripts/calibration_budget.py':continue
        if '43001' in m['text'] and ('calibration_only' in m['text'] or 'seed!=43001' in m['text'] or 'seed: int = 43001' in m['text']):continue
        conflicts.append(m)
    data=ROOT/'results_main_rebuild_r1/data/traffic'
    cols=['unit_id','spatial_id','absolute_time','time_index','target_group','opportunity_stratum','split','support_flag']
    catalogue=pd.read_parquet(data/'atomic_units.parquet',columns=cols)
    public=catalogue.to_dict('records')
    identity=hashlib.sha256(json.dumps(public,sort_keys=True,default=str).encode()).hexdigest()
    report=dict(audited_at_utc=datetime.now(timezone.utc).isoformat(),seed=43001,scanned_text_files=scanned,
        matched_lines=matches,seed_named_assets=names,unreadable=skipped,review_required=conflicts,
        status='NO_PRIOR_SELECTION_OR_EXECUTION_FOUND' if not conflicts and not names and not skipped else 'REVIEW_REQUIRED',
        scope=[str(r) for r in roots],exclusions=sorted(ignore),binary_limit='binary filenames audited; seed identity checked in companion metadata, not binary byte-string search',
        public_catalogue=dict(path=str(data/'atomic_units.parquet'),columns=cols,rows=len(catalogue),
            frozen_before_window_0=True,publication_at_utc=datetime.now(timezone.utc).isoformat(),
            role='deployment target/support metadata only; no TEST values',identity=identity,
            target_rule='same frozen supported test spatial-by-TOD mass as historical target, now explicitly published before run',
            clients=int(catalogue.spatial_id.nunique()),train_rows=int((catalogue.split=='train').sum())))
    (OUT/'SEED_AND_INPUT_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    catalogue.to_parquet(OUT/'PUBLIC_CATALOGUE.parquet',index=False)
    print(json.dumps(report,ensure_ascii=False,default=str))

if __name__=='__main__':main()
