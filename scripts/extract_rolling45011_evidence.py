"""Descriptive extraction from completed logs only; no replay or fitting."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'results_observed_feedback_rolling_45011_20261014_s2'
rows=json.loads((out/'MERGED_DECISION_METRICS.json').read_text())
plans=[json.loads(x) for x in (out/'ROLLING_COST_PLANS.jsonl').read_text().splitlines()]
summary=json.loads((out/'VALIDATION_AND_SUMMARY.json').read_text())
records=json.loads((out/'OPERATION_RECORDS.json').read_text())
def compact(x):
    return {k:x[k] for k in ('time','window','action','reason','B','components','shadow','actual_request_root_upper')}
cases=[compact(x) for x in rows if 20<x['time']<100 and x['action']!=x['shadow']['no_Q_stop']]
result=dict(no_Q_cases=cases,no_Q_fraction_all_regular=len(cases)/799,
    no_Q_fraction_nonforced=len(cases)/summary['nonforced_rows'],
    frozen_reference='No feature, parameter, threshold, seed or gate changed using these outcomes',
    first_checkpoint_bytes=plans[0]['current']['checkpoint_bytes'],final_checkpoint_bytes=summary['final_checkpoint_sizes'],
    original_checkpoint_bytes=[6301614,4134777],
    queue_max=max(x['current']['private_queue'] for x in plans),P_max_at_checkpoints=max(x['current']['P'] for x in plans),
    F_max_at_checkpoints=max(x['current']['F'] for x in plans),
    P2_cache_cost_scope='Full online root requests include solve/cache lookup, controller and actual apply; independent solver-only CPU not separately measured',
    source_of_support='One linked device/network stratum per class; no independent cross-product support or calibration demonstrated')
detail={}
for row in records:
    key=row['category']+'/'+row['operation_kind'];bucket=detail.setdefault(key,dict(count=0,root_difference=0.,root_upper_sum=0.,wall=0.,max_root_upper=0.))
    bucket['count']+=1;bucket['root_difference']+=row['request_root_difference'];bucket['root_upper_sum']+=row['root_upper_CPU'];bucket['wall']+=row['wall'];bucket['max_root_upper']=max(bucket['max_root_upper'],row['root_upper_CPU'])
result['operation_breakdown']=detail
(out/'DESCRIPTIVE_MECHANISM_AND_COST.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
