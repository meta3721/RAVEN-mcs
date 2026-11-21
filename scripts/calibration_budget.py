"""Meter only the separately authorized first calibration batch; no queue."""
from pathlib import Path
import argparse, json, sys, time
from validate_conditional_bundle_b0 import run_accounted, protect, save

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    p.add_argument('--label',required=True);p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args();out=a.out.resolve();out.relative_to(ROOT)
    if not out.exists():
        out.mkdir()
        assets=protect()
        import hashlib
        for folder in ('ccf-review-report/conditional_bundle_b0_20261012_223821','results_conditional_bundle_b0_20261012_223821'):
            for f in (ROOT/folder).glob('*'):
                if f.is_file():assets[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
        save(out/'PROTECTED_BEFORE.json',assets)
        save(out/'BUDGET.json',dict(limit_cpu_seconds=3600,interactive_allowance_seconds=120,
            charged_to='original_5_CPU_hour_calibration_application',runs=[],gpu=0,
            max_local_sgd_steps=5000,authorized_seed=43001,target_T=100,
            remaining_seven_authorized=False,B1_authorized=False,formal_authorized=False))
    ledger=json.loads((out/'BUDGET.json').read_text());used=120+sum(r['process_tree_cpu_seconds']+r['monitor_cpu_seconds'] for r in ledger['runs'])+sum(x['charged_cpu_seconds'] for x in ledger.get('supplemental_charges',[]))
    if used>=3600:raise RuntimeError('BATCH_CPU_EXHAUSTED')
    command=a.command
    if command and command[0]=='--':command=command[1:]
    result=run_accounted(command,out/(a.label+'.log'),cpu_limit=3600-used-10,wall_limit=14400)
    ledger['runs'].append(result);save(out/'BUDGET.json',ledger)
    import hashlib
    assets=json.loads((out/'PROTECTED_BEFORE.json').read_text())
    changed=[f for f,h in assets.items() if hashlib.sha256(Path(f).read_bytes()).hexdigest()!=h]
    save(out/(a.label+'-preservation.json'),dict(files=len(assets),changed=changed))
    print(json.dumps(result),flush=True)
    if changed:raise RuntimeError('HISTORICAL_ASSET_CHANGED')
    sys.exit(result['returncode'])

if __name__=='__main__':main()
