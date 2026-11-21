"""Explicit single-seed calibration_only entry; never loops over seeds."""
import argparse,json
from pathlib import Path

if __name__=='__main__':
    # Windows planning workers import __mp_main__. Keep real training/data
    # imports in the approved parent, rather than every planning child.
    from raven_mcs.experiments.calibration_first import acquire_first
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['calibration_only'],required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];out=a.out.resolve();out.relative_to(root)
    budget=json.loads((out/'BUDGET.json').read_text())
    used=budget['interactive_allowance_seconds']+sum(r['process_tree_cpu_seconds']+r['monitor_cpu_seconds'] for r in budget['runs'])
    acquire_first(root,out,cpu_remaining=budget['limit_cpu_seconds']-used-30)
