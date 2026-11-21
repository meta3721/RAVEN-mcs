"""Bounded B0 checks only: no training, eventtrace execution or replay queues."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from raven_mcs.control.process_budget import ProcessTreeBudget


def save(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')


def protect():
    previous=ROOT/'results_reachability_method_prep_20261012_220855/SOURCE_INVENTORY.json'
    paths=[Path(x['path']) for x in json.loads(previous.read_text(encoding='utf-8'))['assets']]
    for directory in ('results_reachability_method_prep_20261012_220855',
                      'ccf-review-report/reachability_method_prep_20261012_220855'):
        paths.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.extend((ROOT/p) for p in ('DESIGN_GATE_ALIGNMENT_REPORT.md','TO_OVERLEAF_paper_tmc_r1_clean/main.tex'))
    paths.extend(ROOT.rglob('STOP_REPORT.md'))
    return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def run_accounted(command,log,*,cpu_limit,wall_limit):
    if os.name == 'nt':
        # Assign the launcher while suspended: its real interpreter and all
        # later (including nested-Job) workers inherit the accounting boundary.
        # Keep the old non-Windows implementation below unchanged.
        from windows_cpu_meter import run_metered
        result = run_metered(command, log, cpu_limit=cpu_limit,
                             wall_limit=wall_limit, cwd=ROOT)
        if not result['audit_passed']:
            raise RuntimeError('RESOURCE_ACCOUNTING_AUDIT_FAILED; see .meter.json')
        return result
    start=time.perf_counter();parent=time.process_time();job=ProcessTreeBudget()
    env=dict(os.environ,PYTHONPATH=str(ROOT/'src'),OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
             OPENBLAS_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTHONHASHSEED='26004')
    with log.open('x',encoding='utf-8') as stream:
        proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
        save(log.with_suffix('.process.json'),dict(pid=proc.pid,command=command))
        try:
            job.attach(proc.pid);limit_reason=None
            while proc.poll() is None:
                cpu=job.cpu_seconds()+time.process_time()-parent
                if cpu>=cpu_limit-.2 or time.perf_counter()-start>wall_limit:
                    limit_reason='cpu' if cpu>=cpu_limit-.2 else 'wall'
                    job.terminate();break
                time.sleep(.02)
            proc.wait()
            return dict(command=command,returncode=proc.returncode,
                process_tree_cpu_seconds=job.cpu_seconds(),monitor_cpu_seconds=time.process_time()-parent,
                wall_seconds=time.perf_counter()-start,limit_reason=limit_reason,log=str(log))
        finally:
            if proc.poll() is None:proc.terminate();proc.wait()
            job.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--initialize',action='store_true')
    parser.add_argument('--check-legacy-manifest-once',action='store_true')
    parser.add_argument('--pytest',nargs='*')
    parser.add_argument('--code-checks',action='store_true')
    parser.add_argument('--label',default='iteration1')
    args=parser.parse_args();out=args.output_dir.resolve()
    out.relative_to(ROOT)
    if args.initialize:
        out.mkdir(parents=True,exist_ok=False)
        before=protect();save(out/'PROTECTED_BEFORE.json',before)
        save(out/'AUTHORIZATION.json',dict(stage='B0',method='conditional-bundle-v2',cpu_limit_seconds=7200,
            charged_to='original_prevalidation_8_cpu_hours',training=0,random_synthetic_replay=0,
            real_control_replay=0,formal_confirmation=False,old_tasks_resumed=False))
        save(out/'BUDGET.json',dict(limit_cpu_seconds=7200,runs=[],interactive_allowance_seconds=300,
                                  training_steps=0,synthetic_replays=0,real_replays=0))
    ledger=json.loads((out/'BUDGET.json').read_text(encoding='utf-8'))
    spent=ledger['interactive_allowance_seconds']+sum(r['process_tree_cpu_seconds']+r['monitor_cpu_seconds'] for r in ledger['runs'])
    if spent>=7200:raise RuntimeError('B0_CPU_BUDGET_EXHAUSTED')
    if args.check_legacy_manifest_once:
        marker=out/'LEGACY_MANIFEST_ATTEMPT.json'
        if marker.exists():raise RuntimeError('only one historical manifest attempt allowed')
        command=[sys.executable,'-X','faulthandler','-c',
            "from pathlib import Path; from raven_mcs.utils.manifest import _git_info; print(_git_info(Path.cwd()),flush=True)"]
        result=run_accounted(command,out/'legacy-manifest-once.log',cpu_limit=min(60,7200-spent),wall_limit=60)
        save(marker,result);ledger['runs'].append(result)
    if args.pytest is not None:
        command=[sys.executable,'-X','faulthandler','-m','pytest',*args.pytest,'-ra',
                 f'--junitxml={out/ (args.label+".xml")}',f'--basetemp={out/(args.label+"-tmp")}']
        env_before=os.environ.get('B0_EVIDENCE_DIR');label_before=os.environ.get('B0_EVIDENCE_LABEL')
        os.environ['B0_EVIDENCE_DIR']=str(out);os.environ['B0_EVIDENCE_LABEL']=args.label
        try:result=run_accounted(command,out/(args.label+'.log'),cpu_limit=min(600,7200-spent),wall_limit=600)
        finally:
            if env_before is None:os.environ.pop('B0_EVIDENCE_DIR',None)
            else:os.environ['B0_EVIDENCE_DIR']=env_before
            if label_before is None:os.environ.pop('B0_EVIDENCE_LABEL',None)
            else:os.environ['B0_EVIDENCE_LABEL']=label_before
        ledger['runs'].append(result)
    if args.code_checks:
        commands=[
            ('syntax',[sys.executable,'-c',
             "import ast; from pathlib import Path; from raven_mcs.control.persistence import computational_sources; "
             "paths=list(computational_sources(Path.cwd()))+list(Path('tests/control_b0').glob('*.py'))+"
             "[Path('scripts/validate_conditional_bundle_b0.py')]; "
             "paths=[p for p in paths if p.suffix=='.py']; "
             "[ast.parse(p.read_text(encoding='utf-8'),filename=str(p)) for p in paths]; print('SYNTAX_OK',len(paths))"]),
            ('environment',[sys.executable,'scripts/verify_run.py','--check-environment'])]
        for suffix,command in commands:
            used=ledger['interactive_allowance_seconds']+sum(x['process_tree_cpu_seconds']+x['monitor_cpu_seconds'] for x in ledger['runs'])
            result=run_accounted(command,out/(args.label+'-'+suffix+'.log'),
                cpu_limit=min(60,7200-used),wall_limit=60)
            ledger['runs'].append(result)
    save(out/'BUDGET.json',ledger)
    protected=json.loads((out/'PROTECTED_BEFORE.json').read_text(encoding='utf-8'))
    changes=[p for p,h in protected.items() if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
    save(out/('preservation-'+args.label+'.json'),dict(files=len(protected),changed=changes))
    if changes:raise RuntimeError(f'HISTORICAL_ASSET_CHANGED:{changes}')
    print(json.dumps(dict(spent_cpu_accounted_seconds=ledger['interactive_allowance_seconds']+
        sum(r['process_tree_cpu_seconds']+r['monitor_cpu_seconds'] for r in ledger['runs']),
        protected_files=len(protected),runs=ledger['runs'][-1:] if ledger['runs'] else []),ensure_ascii=False))


if __name__=='__main__':main()
