"""Audit seed identity, never reads private value tables for selection."""
import os,re,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results_observed_feedback_acquisition_45011_20261014'
pattern=re.compile(rb'(?<![\d.])45011(?![\d.])');matches=[];named=[];errors=[];count=0
skip={'.git','.venv','.venv_new','node_modules','__pycache__','.codex','.agents','raw','site-packages','data','datasets','client_measurements'}
allowed_docs={'ccf-review-report','research-protocols','.codex-remote-attachments'}
for base in (ROOT,Path('C:/Users/szr/Desktop/record/1')):
    for directory,dirs,files in os.walk(base):
        dirs[:]=[d for d in dirs if d not in skip and not d.startswith('.venv') and Path(directory)/d!=OUT]
        for name in files:
            path=Path(directory)/name
            if '45011' in name and path.suffix not in {'.py','.md','.txt'}:named.append(str(path))
            if path.suffix.lower() not in {'.json','.jsonl','.md','.yaml','.yml','.toml','.py','.txt','.tex'}:continue
            if path in {ROOT/'src/raven_mcs_observed_feedback/authorization.py',ROOT/'src/raven_mcs_observed_feedback/acquisition.py'}:continue # Created for this approved batch only.
            if path.name.startswith(('observed_feedback_acquisition','audit_observed_feedback_seed45011')):continue
            count+=1
            try:
                # Chunked C-regex scanning, not Python line iteration through large state/decision logs.
                with path.open('rb') as f:
                    offset=0;tail=b''
                    while True:
                        chunk=f.read(1024*1024)
                        if not chunk:break
                        block=tail+chunk
                        for m in pattern.finditer(block) if b'45011' in block else ():
                            context=block[max(0,m.start()-90):m.end()+90]
                            matches.append(dict(path=str(path),byte_offset=offset-len(tail)+m.start(),text=context.decode('utf-8','replace'),
                                role='proposal_document' if path.suffix in {'.md','.txt','.tex'} else 'REVIEW'))
                        tail=block[-128:];offset+=len(chunk)
            except OSError as exc:errors.append(dict(path=str(path),error=repr(exc)))
conflicts=[x for x in matches if x['role']=='REVIEW'];status='NO_PRIOR_SELECTION_OR_EXECUTION_FOUND' if not conflicts and not named and not errors else 'REVIEW_REQUIRED'
with (OUT/'SEED_REVIEW.json').open('x') as f:json.dump(dict(status=status,seed=45011,files_scanned=count,matches=matches,named_assets=named,
    conflicts=conflicts,unreadable=errors,binary_limit='seed named assets and companion text identity; binary content not searched'),f,indent=2)
print(json.dumps(dict(status=status,files=count,matches=len(matches),conflicts=len(conflicts),named=len(named))))
